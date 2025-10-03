from fastapi import FastAPI, HTTPException, Query
from app.analyzer import NASAWeatherAnalyzer
from app.schemas import WeatherRequest
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(title="NASA Weather Probability API")

analyzer = NASAWeatherAnalyzer()

@app.post("/analyze")
async def analyze_weather(request: WeatherRequest, export: str = Query("none", enum=["none", "json", "csv"])):
    try:
        # Fetch historical data
        raw_data = analyzer.fetch_historical_data(request.latitude, request.longitude)
        df = analyzer.process_historical_data(raw_data)
        stats = analyzer.analyze_future_date(df, request.future_date)

        # Export format
        if export == "json":
            result = analyzer.export_to_json(request.latitude, request.longitude, request.future_date, stats)
            return JSONResponse(content=result)

        elif export == "csv":
            csv_content = analyzer.export_to_csv(request.latitude, request.longitude, request.future_date, stats)
            return PlainTextResponse(content=csv_content, media_type="text/csv")

        else:
            # Return report as plain text
            report = analyzer.generate_report(request.latitude, request.longitude, request.future_date, stats)
            return PlainTextResponse(content=report, media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
