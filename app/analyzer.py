import requests
import pandas as pd
import numpy as np
from datetime import datetime
import json

class NASAWeatherAnalyzer:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.current_year = datetime.now().year

    def export_to_json(self, latitude, longitude, future_date, stats):
        if isinstance(future_date, str):
            future_date = datetime.strptime(future_date, '%Y-%m-%d')
        output = {
            'metadata': {
                'location': {'latitude': latitude, 'longitude': longitude},
                'target_date': future_date.strftime('%Y-%m-%d'),
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'data_source': 'NASA POWER API',
                'sample_size': stats['sample_size']
            },
            'statistics': stats
        }
        return output

    def export_to_csv(self, latitude, longitude, future_date, stats):
        # نفس اللي عندك
        import io
        rows = []
        rows.append(['Metric', 'Value', 'Unit'])
        rows.append(['Latitude', latitude, 'degrees'])
        rows.append(['Longitude', longitude, 'degrees'])
        rows.append(['Target Date', future_date, ''])
        rows.append(['Sample Size', stats['sample_size'], 'observations'])
        # باقي القيم زي ما هي
        df = pd.DataFrame(rows)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        return buffer.getvalue()

    def fetch_historical_data(self, latitude, longitude, start_year=None, end_year=None):
        """
        Fetch historical weather data from NASA POWER API

        Parameters:
        - latitude: float (-90 to 90)
        - longitude: float (-180 to 180)
        - start_year: int (default: current_year - 10)
        - end_year: int (default: current_year - 1)
        """
        if start_year is None:
            start_year = self.current_year - 10
        if end_year is None:
            end_year = self.current_year - 1

        # Parameters we want to fetch
        parameters = [
            'T2M',  # Temperature at 2 Meters (°C)
            'QV2M',  # Specific Humidity at 2 Meters (g/kg)
            'U10M',  # Wind Speed at 10 Meters (m/s)
            'PS',  # Surface Pressure (kPa)
            'PRECTOTCORR'  # Precipitation (mm/day)
        ]

        params = {
            'parameters': ','.join(parameters),
            'community': 'AG',  # Agroclimatology community
            'longitude': longitude,
            'latitude': latitude,
            'start': f"{start_year}0101",
            'end': f"{end_year}1231",
            'format': 'JSON'
        }

        print(f"Fetching data from NASA POWER API...")
        print(f"Location: ({latitude}, {longitude})")
        print(f"Period: {start_year} - {end_year}")

        try:
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if 'properties' in data and 'parameter' in data['properties']:
                return data['properties']['parameter']
            else:
                raise Exception("Unexpected API response format")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching data from NASA API: {e}")

    def process_historical_data(self, raw_data):
        """Convert raw API data to pandas DataFrame"""
        df_dict = {}

        for param, values in raw_data.items():
            df_dict[param] = pd.Series(values)

        df = pd.DataFrame(df_dict)
        df.index = pd.to_datetime(df.index, format='%Y%m%d')

        # Add day of year column
        df['day_of_year'] = df.index.dayofyear
        df['month'] = df.index.month
        df['day'] = df.index.day

        return df
    def analyze_future_date(self, df, future_date):
        """
        Analyze historical data for the specific day of year

        Parameters:
        - df: DataFrame with historical data
        - future_date: datetime object or string (YYYY-MM-DD)
        """
        if isinstance(future_date, str):
            future_date = datetime.strptime(future_date, '%Y-%m-%d')

        target_month = future_date.month
        target_day = future_date.day

        # Filter data for this specific date across all years
        historical_for_date = df[(df['month'] == target_month) & (df['day'] == target_day)]

        if len(historical_for_date) == 0:
            raise Exception(f"No historical data found for {target_month}/{target_day}")

        # Calculate statistics
        stats = {}

        # Temperature analysis (convert to Fahrenheit for display)
        if 'T2M' in df.columns:
            temps_c = historical_for_date['T2M'].dropna()
            temps_f = temps_c * 9 / 5 + 32
            stats['temperature'] = {
                'avg_celsius': round(temps_c.mean(), 1),
                'avg_fahrenheit': round(temps_f.mean(), 1),
                'min_fahrenheit': round(temps_f.min(), 1),
                'max_fahrenheit': round(temps_f.max(), 1),
                'std_fahrenheit': round(temps_f.std(), 1),
                'very_hot_prob': round((temps_f > 90).sum() / len(temps_f) * 100, 1),
                'very_cold_prob': round((temps_f < 32).sum() / len(temps_f) * 100, 1),
            }

        # Rain / Precipitation
        if 'PRECTOTCORR' in df.columns:
            precip = historical_for_date['PRECTOTCORR'].dropna()
            stats['rain'] = {
                'avg_mm': round(precip.mean(), 2),
                'max_mm': round(precip.max(), 2),
                'rainy_day_prob': round((precip > 0.1).sum() / len(precip) * 100, 1),
                'heavy_rain_prob': round((precip > 10).sum() / len(precip) * 100, 1)
            }

        # Specific humidity analysis
        if 'QV2M' in df.columns:
            humidity = historical_for_date['QV2M'].dropna()
            stats['specific_humidity'] = {
                'avg_g_kg': round(humidity.mean(), 2),
                'min_g_kg': round(humidity.min(), 2),
                'max_g_kg': round(humidity.max(), 2),
                'high_humidity_prob': round((humidity > 15).sum() / len(humidity) * 100, 1),
            }

        # Wind analysis (U10M - wind at 10 meters)
        if 'U10M' in df.columns:
            wind = historical_for_date['U10M'].dropna()
            wind_mph = wind * 2.237  # Convert m/s to mph
            stats['wind'] = {
                'avg_ms': round(wind.mean(), 1),
                'avg_mph': round(wind_mph.mean(), 1),
                'max_mph': round(wind_mph.max(), 1),
                'very_windy_prob': round((wind_mph > 10).sum() / len(wind_mph) * 100, 1),
                'extreme_wind_prob': round((wind_mph > 15).sum() / len(wind_mph) * 100, 1),
            }

        # Surface pressure analysis
        if 'PS' in df.columns:
            pressure = historical_for_date['PS'].dropna()
            pressure_mb = pressure * 10  # Convert kPa to mb (hPa)
            stats['pressure'] = {
                'avg_kpa': round(pressure.mean(), 2),
                'avg_mb': round(pressure_mb.mean(), 1),
                'min_mb': round(pressure_mb.min(), 1),
                'max_mb': round(pressure_mb.max(), 1),
                'low_pressure_prob': round((pressure_mb < 1010).sum() / len(pressure_mb) * 100, 1),
            }

        # Calculate "very uncomfortable" conditions
        # (High temp + high specific humidity OR extreme cold)
        if 'T2M' in df.columns and 'QV2M' in df.columns:
            temps_f = historical_for_date['T2M'] * 9 / 5 + 32
            spec_humidity = historical_for_date['QV2M']

            # High temp + high humidity OR extreme cold
            uncomfortable = ((temps_f > 85) & (spec_humidity > 15)) | (temps_f < 35)
            stats['comfort'] = {
                'very_uncomfortable_prob': round(uncomfortable.sum() / len(uncomfortable) * 100, 1)
            }

        stats['sample_size'] = len(historical_for_date)

        return stats
    def generate_report(self, latitude, longitude, future_date, stats):
        """Generate a human-readable report"""
        if isinstance(future_date, str):
            future_date = datetime.strptime(future_date, '%Y-%m-%d')

        report = []
        report.append("=" * 70)
        report.append("NASA WEATHER PROBABILITY REPORT")
        report.append("=" * 70)
        report.append(f"\nLocation: Latitude {latitude}°, Longitude {longitude}°")
        report.append(f"Target Date: {future_date.strftime('%B %d, %Y')}")
        report.append(f"Analysis based on {stats['sample_size']} historical observations")
        report.append("\n" + "-" * 70)

        # Temperature
        if 'temperature' in stats:
            temp = stats['temperature']
            report.append("\n📊 TEMPERATURE:")
            report.append(f"  • Average: {temp['avg_fahrenheit']}°F ({temp['avg_celsius']}°C)")
            report.append(f"  • Historical Range: {temp['min_fahrenheit']}°F to {temp['max_fahrenheit']}°F")
            report.append(f"  • Probability of VERY HOT (>90°F): {temp['very_hot_prob']}%")
            report.append(f"  • Probability of VERY COLD (<32°F): {temp['very_cold_prob']}%")

        # Rain
        if 'rain' in stats:
            rain = stats['rain']
            report.append("\n🌧️ RAIN:")
            report.append(f"  • Avg rainfall: {rain['avg_mm']} mm")
            report.append(f"  • Max rainfall: {rain['max_mm']} mm")
            report.append(f"  • Probability of rain: {rain['rainy_day_prob']}%")
            report.append(f"  • Probability of heavy rain (>10mm): {rain['heavy_rain_prob']}%")

        # Specific Humidity
        if 'specific_humidity' in stats:
            hum = stats['specific_humidity']
            report.append("\n💧 SPECIFIC HUMIDITY:")
            report.append(f"  • Average: {hum['avg_g_kg']} g/kg")
            report.append(f"  • Historical Range: {hum['min_g_kg']} - {hum['max_g_kg']} g/kg")
            report.append(f"  • Probability of high humidity (>15 g/kg): {hum['high_humidity_prob']}%")

        # Wind
        if 'wind' in stats:
            wind = stats['wind']
            report.append("\n💨 WIND (at 10m height):")
            report.append(f"  • Average Speed: {wind['avg_mph']} mph ({wind['avg_ms']} m/s)")
            report.append(f"  • Maximum recorded: {wind['max_mph']} mph")
            report.append(f"  • Probability of VERY WINDY : {wind['very_windy_prob']}%")
            report.append(f"  • Probability of EXTREME WIND (>30mph): {wind['extreme_wind_prob']}%")

        # Surface Pressure
        if 'pressure' in stats:
            pres = stats['pressure']
            report.append("\n🌡️  SURFACE PRESSURE:")
            report.append(f"  • Average: {pres['avg_mb']} mb ({pres['avg_kpa']} kPa)")
            report.append(f"  • Historical Range: {pres['min_mb']} - {pres['max_mb']} mb")
            report.append(f"  • Probability of low pressure (<1010mb): {pres['low_pressure_prob']}%")

        # Liquid Precipitation
        if 'liquid_precipitation' in stats:
            precip = stats['liquid_precipitation']
            report.append("\n🌧️  LIQUID PRECIPITATION:")
            report.append(f"  • Average: {precip['avg_inches']} inches ({precip['avg_mm']} mm)")
            report.append(f"  • Maximum recorded: {precip['max_mm']} mm")
            report.append(f"  • Probability of rainy day (>2.5mm): {precip['rainy_day_prob']}%")
            report.append(f"  • Probability of VERY WET (>10mm): {precip['very_wet_prob']}%")
            report.append(f"  • Probability of heavy rain (>25mm): {precip['heavy_rain_prob']}%")

        # Total Precipitable Water
        if 'precipitable_water' in stats:
            tpw = stats['precipitable_water']
            report.append("\n💦 TOTAL PRECIPITABLE WATER:")
            report.append(f"  • Average: {tpw['avg_kg_m2']} kg/m²")
            report.append(f"  • Historical Range: {tpw['min_kg_m2']} - {tpw['max_kg_m2']} kg/m²")
            report.append(f"  • Probability of high atmospheric moisture (>40 kg/m²): {tpw['high_moisture_prob']}%")

        # Comfort
        if 'comfort' in stats:
            comfort = stats['comfort']
            report.append("\n😓 COMFORT LEVEL:")
            report.append(f"  • Probability of VERY UNCOMFORTABLE conditions: {comfort['very_uncomfortable_prob']}%")

        report.append("\n" + "=" * 70)
        report.append("\nNOTE: Probabilities are based on historical data, not forecasts.")
        report.append("=" * 70)

        return "\n".join(report)