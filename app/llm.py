import os
from dotenv import load_dotenv

load_dotenv()
import google.generativeai as genai

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def interact_llm(activity=None, weather_values=None):
    values_text = "\n".join(
        [f"- {key}: {val}" for key, val in weather_values.items()]
    )if weather_values else "No weather values provided yet."
    # Build the prompt
    initial_prompt = f"""
You are a weather activity assistant.

The user wants to know if they can do the activity: **{activity}**.  

You have access to the following weather values:
{values_text}

Current weather data:
{values_text if values_text else "No weather values provided yet."}

Your tasks:
1. Validate whether the activity can be done based on the current weather values.  
   - Example: If precipitation is high → not suitable for hiking.  
   - Example: If strong winds → not suitable for fishing/boating.  
   - Example: If temperature is extreme → unsafe for outdoor activity.  
2. If the activity is not suitable, suggest at least **2 alternative activities** based on the same weather data.  
3. Keep your response clear, concise, and user-friendly.
"""

    professional_prompt = f"""
You are **Skyra**, a professional and intelligent weather insight assistant
for the NASA Weather Intelligence Platform.

Your goal is to generate a clear, professional summary based on NASA weather data.

Context:
- User’s activity of interest: **{activity if activity else "Not specified"}**
- Weather data available:
{values_text if values_text else "No weather data provided."}

Your tasks:
1. If an **activity is specified**, analyze whether current conditions are suitable, risky, or unsafe for that activity.
   - Mention key factors such as temperature, precipitation, wind speed, and pressure.
   - If unsuitable, recommend **2 alternative activities** (indoor or outdoor depending on conditions).
2. If **no activity is provided**, create a short and professional **weather summary only**, focusing on:
   - Temperature range
   - Wind conditions
   - Precipitation or cloud cover
   - Overall comfort or stability of weather
3. The response must be:
   - Written in a **neutral, analytical, and human-like tone**
   - Formatted like a weather report, **not a chatbot message**
   - Short and organized (max 3 short paragraphs)
4. Never mention AI, LLM, or that you are a chatbot. The response should read like a system-generated weather summary.

Example output (if activity exists):
"🌤️ **Weather Summary for Hiking**
Conditions are moderately suitable for hiking today. Temperatures range from 20°C to 26°C with light winds (6 mph). Occasional clouds are expected but no significant rainfall.  
⚠️ If trails become slippery, consider safer alternatives like indoor rock climbing or a short nature walk instead."

Example output (if no activity):
"🌦️ **Weather Overview**
Temperatures range from 22°C to 27°C with mild winds and low precipitation chances.  
Overall, it’s a comfortable and partly cloudy day with good air stability — ideal for most outdoor plans."
"""

    try:
        # Create the model
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # Generate content
        response = model.generate_content(professional_prompt)

        if not response or not hasattr(response, 'text'):
            raise ValueError("Invalid response from GenAI API")
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't process your request due to an error: {str(e)}"