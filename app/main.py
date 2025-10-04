import uuid

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from app.analyzer import NASAWeatherAnalyzer
from app.chatbot import chatbot_llm
from app.llm import interact_llm
from app.schemas import WeatherRequest, ChatRequest
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(title="NASA Weather Probability API")

analyzer = NASAWeatherAnalyzer()
origins = [
    "https://skyra-iota.vercel.app",  # frontend dev server
    "http://localhost:3000",          # Common React/Next/Vite default port
    "http://localhost:8000",          # Common FastAPI/local development port
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # origins that are allowed
    allow_credentials=True,
    allow_methods=["*"],         # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # allow all headers
)
@app.post("/analyze")
async def analyze_weather(request: WeatherRequest, export: str = Query("json", enum=["json", "csv", "none"])):
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
#---------------------------------------------------------------------------------------------------------------------------------

SESSIONS = {}
def get_or_create_session(session_id: str = None):
    if not session_id or session_id not in SESSIONS:
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = []
    return session_id

def add_to_history(session_id: str, user_message: str, bot_reply: str):
    SESSIONS[session_id].append(f"User: {user_message}")
    SESSIONS[session_id].append(f"Bot: {bot_reply}")
    return SESSIONS[session_id]

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    session_id = get_or_create_session(request.session_id)

    history_text = "\n".join(SESSIONS[session_id])

    bot_reply = chatbot_llm(
        activity=request.activity,
        weather_values=request.weather_values,
        history=history_text,
        user_message=request.user_message
    )

    add_to_history(session_id, request.user_message, bot_reply)

    return JSONResponse(content={
        "session_id": session_id,
        "user_message": request.user_message,
        "bot_reply": bot_reply,
        "history": SESSIONS[session_id]
    })
