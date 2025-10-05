# 🌤️ Skyra

**Skyra** is the backend service powering the **Skyra Project** —  
an intelligent weather-aware activity assistant that helps users plan their activities safely and efficiently.

By leveraging NASA’s historical and forecast weather data, Skyra analyzes the **location**, **time**, and **activity type**  
to determine whether the conditions are suitable — and if not, it suggests smarter alternatives.

---

## ✨ Features

- ✅ **Smart Weather Evaluation** – Checks if an activity (e.g., hiking, diving, cycling) is suitable based on temperature, precipitation, wind speed, and more.  
- 🔄 **AI-Powered Recommendations** – Suggests alternative activities when the weather is unfavorable.  
- 🌍 **Location & Time Awareness** – Supports user-specified coordinates and date/time.  
- 🤖 **LLM Integration** – Generates natural language weather summaries and activity suggestions.
---

## 📂 Project Structure

```bash
Skyra-Backend/
├── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── schemas.py        # Data models
│   ├── analyzer.py      # Weather/activity logic
│   ├── llm.py           # Prompt & AI assistant
|   ├── chatbot.py       # chatbot assistant
│   └── utils.py          # Variables configuration
├── requirements.txt
├── .gitignore
├── README.md
└── other project files...
```
# ⚙️ Requirements & Installation
- Prerequisites
- Python >= 3.9
- Dependencies listed in requirements.txt

# Local Setup
```bash
Clone the repository
git clone https://github.com/Skyra-nasa/Skyra-Backend-2.git
cd Skyra-Backend
```
## Create and activate a virtual environment
```
python -m venv venv
```
## On Windows
```
venv\Scripts\activate
```
## On Linux/Mac
```
source venv/bin/activate
```
# Install dependencies
```
pip install -r requirements.txt
```
## 🚀 Running the Application

Run the FastAPI app with Uvicorn:
```
uvicorn app.main:app --reload
```

## Then open your browser at:
http://localhost:8000


## Interactive API docs are available at:
http://localhost:8000/docs

## 💡 How It Works

User provides:

Activity (e.g., "hiking", "swimming")

Location (city or coordinates)

Time (date/hour)

Backend retrieves forecasted weather data.

AI model evaluates:

✅ YES → Activity is safe and suitable

❌ NO → Unsafe or unsuitable → Suggest at least 2 alternatives
