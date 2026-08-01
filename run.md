# How to Run the Project

This guide provides the exact commands to start and test the **Resume Scanner & ATS Predictor** application in PowerShell or Command Prompt.

---

> [!TIP]
> **PowerShell Note:** In PowerShell, always include `.\` at the start of relative paths (e.g. `.\.venv\Scripts\python.exe`), or activate the environment first.

---

## 🚀 Option 1: Quick Start (Single Command)

To run both the **FastAPI Backend** and **Streamlit Dashboard UI** at the same time:

### PowerShell:
```powershell
.\.venv\Scripts\python.exe run.py
```

### Command Prompt (CMD):
```cmd
.venv\Scripts\python.exe run.py
```

---

## 🛠️ Option 2: Run after Activating Virtual Environment

Alternatively, activate the virtual environment once in your terminal:

### In PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell blocks execution policies, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

### In Command Prompt (CMD):
```cmd
.venv\Scripts\activate.bat
```

Once activated, you can simply run standard `python` / `streamlit` commands:

```powershell
# Run single launcher
python run.py

# Or run backend in terminal 1:
python -m uvicorn app.main:app --reload --port 8000

# And frontend in terminal 2:
streamlit run web/streamlit_app.py
```

---

## 🛠️ Option 3: Manual Start in Separate Terminals

If launching without activating the virtual environment:

### Terminal 1: Backend Server (FastAPI)
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend Dashboard (Streamlit)
```powershell
.\.venv\Scripts\python.exe -m streamlit run web/streamlit_app.py
```

---

## 🧪 Running Tests

To run the automated `pytest` test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

---

## ⚙️ Environment Configuration

Ensure your `.env` file exists in the root directory (copied from `.env.example`):

```env
GEMINI_MOCK=true
GEMINI_API_KEY=
```

> **Note**: Setting `GEMINI_MOCK=true` allows full offline testing without needing an active Google Gemini API key.

