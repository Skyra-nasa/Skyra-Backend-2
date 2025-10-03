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

    try:
        # Create the model
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Generate content
        response = model.generate_content(initial_prompt)


        if not response or not hasattr(response, 'text'):
            raise ValueError("Invalid response from GenAI API")
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't process your request due to an error: {str(e)}"