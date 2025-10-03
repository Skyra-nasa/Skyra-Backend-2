from fastapi import FastAPI, HTTPException, Query
from app.analyzer import NASAWeatherAnalyzer
from app.llm import interact_llm
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

        # interact with llm
        summary_message = interact_llm(request.activity, stats)

        # Export format
        if export == "json":
            result = analyzer.export_to_json(request.latitude, request.longitude, request.future_date, stats)
            result["llm_summary"] = summary_message
            return JSONResponse(content=result)

        elif export == "csv":
            csv_content = analyzer.export_to_csv(request.latitude, request.longitude, request.future_date, stats)
            csv_content = f"# Activity Analysis\n# {summary_message}\n\n" + csv_content
            return PlainTextResponse(content=csv_content, media_type="text/csv")

        else:
            # Return report as plain text
            report = analyzer.generate_report(request.latitude, request.longitude, request.future_date, stats)
            final_report = f"{report}\n\n🤖 Activity Recommendation:\n{summary_message}"
            return PlainTextResponse(content=final_report, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
