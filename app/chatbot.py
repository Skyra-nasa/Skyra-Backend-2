import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def chatbot_llm(activity=None, weather_values=None, history=None, user_message=None):

    values_text = "\n".join(
        [f"- {key}: {val}" for key, val in weather_values.items()]
    ) if weather_values else "No weather values provided yet."

    initial_prompt = f"""
You are a weather activity assistant chatbot.

Activity of interest: **{activity if activity else "Not specified"}**

Weather data available:
{values_text}

Conversation history:
{history if history else "No previous conversation."}

User message:
{user_message}

Your tasks:
1. Answer the user clearly based on the weather values and context.
2. If the weather is not suitable for the requested activity, suggest at least 2 alternatives.
3. Keep answers concise, user-friendly, and conversational.
"""
    professional_prompt = f"""
    You are **Skyra**, a professional weather activity assistant chatbot
    for the NASA Weather Insight web application.

    Your role:
    - Help users understand weather conditions for their selected activity.
    - Give smart, friendly, and well-structured responses.

    Context:
    Activity of interest: **{activity if activity else "Not specified"}**

    Weather data summary:
    {values_text}

    Conversation history:
    {history if history else "No previous conversation."}

    User message:
    {user_message}

    Your objectives:
    1. Provide a clear, natural response based on the given weather data and activity.
    2. If the current weather is not suitable for the selected activity, suggest at least 2 alternative outdoor or indoor activities that match the situation.
    3. If the user asks about something unrelated to weather or activities, reply politely with a short professional message such as:
       - "I’m your weather activity assistant — would you like me to check if the weather suits a specific activity?"
       - or "I can help you understand today’s weather or recommend activities for this condition."
    4. Keep all answers concise, engaging, and easy to read (max 3 short paragraphs).
    5. Always sound polite, professional, and helpful — like a friendly guide.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(professional_prompt)

        if not response or not hasattr(response, 'text'):
            raise ValueError("Invalid response from GenAI API")
        return response.text.strip()
    except Exception as e:
        return f"Sorry, I couldn't process your request due to an error: {str(e)}"