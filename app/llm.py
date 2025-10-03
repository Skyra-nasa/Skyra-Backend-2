import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def interact_llm(activity: str, weather_values: dict = None):
    """
    Interacts with Google Gemini to check if a given activity is suitable
    based on weather data. If not suitable, suggests alternatives.
    
    Args:
        activity (str): The user’s planned activity.
        weather_values (dict): Dict of weather stats (e.g., {"T2M": 25.3, "PS": 1013}).
        location (str): Human-readable location (optional).
        props (dict): Metadata about variables (name, units, conversion).
    """

    # Fallback if props not provided
    if props is None:
        props = {
            "T2M": {"name": "Temperature at 2m", "units": "K", "converted_units": "°C",
                    "conversion": lambda v: v - 273.15},
            "QV2M": {"name": "Specific Humidity at 2m", "units": "kg/kg", "converted_units": "g/kg",
                     "conversion": lambda v: v * 1000},
            # add other vars you support...
        }

    # Build variables description
    variables_desc = []
    for key, val in props.items():
        desc = f"- {val['name']} ({key}): {val['units']} → {val['converted_units']}"
        variables_desc.append(desc)
    variables_text = "\n".join(variables_desc)

    # Build current weather values text
    values_text = "No weather values provided yet."
    if weather_values:
        formatted = []
        for key, value in weather_values.items():
            if key in props:
                conv = props[key].get("conversion")
                try:
                    if conv:
                        converted = conv(value)
                        formatted.append(
                            f"- {props[key]['name']} ({key}): {value:.2f} {props[key]['units']} "
                            f"≈ {converted:.2f} {props[key]['converted_units']}"
                        )
                    else:
                        formatted.append(
                            f"- {props[key]['name']} ({key}): {value:.2f} {props[key]['units']}"
                        )
                except Exception:
                    formatted.append(
                        f"- {props[key]['name']} ({key}): {value:.2f} {props[key]['units']} (conversion failed)"
                    )
        if formatted:
            values_text = "\n".join(formatted)

    # Prompt construction
    system_prompt = "You are a weather activity assistant."
    user_prompt = f"""
The user wants to know if they can do the activity: **{activity}**.
Location: {location if location else "unspecified"}.

You have access to the following weather variables:
{variables_text}

Current weather data:
{values_text}

Your tasks:
1. Validate whether the activity can be done based on the current weather values.  
2. If the activity is not suitable, suggest at least **2 alternative activities**.  
3. Keep your response clear, concise, and user-friendly.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content([
            {"role": "system", "parts": [system_prompt]},
            {"role": "user", "parts": [user_prompt]}
        ])

        # Safe response extraction
        if response and hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text

        return "No valid response text returned from the model."

    except Exception as e:
        return f"Sorry, I couldn't process your request due to an error: {str(e)}"
