# Translit-keyboard

Translit-keyboard is a web application that lets users type in one script (like English/Roman letters) and get transliterated text in an Indian language script.  
It has a backend API, a React frontend, and some ML components for transliteration.

---

## Features

- ✏️ Type phonetically and get text in the target language script  
- 🌐 Backend APIs for transliteration, TTS, STT, and language handling  
- 🧠 ML-based transliteration logic in a separate `ml` module  
- 💻 Simple web UI built with React + TypeScript  

---

## Project Structure

- `backend/` – FastAPI (or similar) backend with REST APIs  
- `frontend/` – React + Vite + TypeScript frontend  
- `ml/` – Scripts and code for training / running the transliteration model  
- `docs/` – Documentation and flow explanations  
- `requirements.txt` – Python dependencies for the backend / ML

---

## Getting Started

### 1. Backend

```bash
cd backend
# create & activate virtual environment (optional but recommended)

# install dependencies
pip install -r ../requirements.txt

# run the backend (example)
uvicorn src.main:app --host 0.0.0.0 --port 8000
