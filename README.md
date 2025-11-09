# Commitment Issues - Back-Office Management System

## Required Packages

### Core Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Core packages
pip install Flask
pip install PyPDF2
pip install PyMuPDF
pip install openai
pip install python-dotenv

# Backend API packages
pip install flask-cors
pip install flasgger
pip install pymongo[srv]
pip install requests
pip install werkzeug

# Optional: Gmail worker (if you want email processing)
pip install google-api-python-client
pip install google-auth-httplib2
pip install google-auth-oauthlib
```

### Or install all at once:

```bash
pip install Flask PyPDF2 PyMuPDF openai python-dotenv flask-cors flasgger "pymongo[srv]" requests werkzeug
```

## How to Run

### 1. Start Backend API (Port 5001)

**Option A: Using Flask CLI**
```bash
python -m flask --app src.main:create_app run --debug --port 5001
```

**Option B: Using run.py**
```bash
python src/BackEnd/run.py
```

**Access:**
- API: http://localhost:5001
- API Docs: http://localhost:5001/apidocs

### 2. Start Frontend Web App (Port 5000)

**Option A: Using Flask CLI**
```bash
python -m flask --app src.FrontEnd.front_end_main run --debug --port 5000
```

**Option B: Using front_end_main.py**
```bash
python src/FrontEnd/front_end_main.py
```

**Access:**
- Web App: http://localhost:5000
- Login: http://localhost:5000/login

### 3. Start Gmail Worker

```bash
python src/gmail_worker/run.py
```

## Quick Start

1. **Install packages** (see above)
2. **Start Backend** in one terminal: `python -m flask --app src.main:create_app run --debug --port 5001`
3. **Start Frontend** in another terminal: `python -m flask --app src.FrontEnd.front_end_main run --debug --port 5000`
4. **Open browser** to http://localhost:5000

## Configuration

- **OpenAI API Key**: Already configured in `src/LLM/llm_functions.py`
- **MongoDB**: Configure connection in `src/DataStorage/db.py`
- **Backend URL**: Default is `http://localhost:5001` (can be changed via `BACKEND_URL` env variable)
