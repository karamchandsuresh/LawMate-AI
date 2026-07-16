from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os

# -----------------------------
# Load .env
# -----------------------------
load_dotenv()

# -----------------------------
# Read API Key
# -----------------------------
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

print("Loaded API Key ends with:", api_key[-4:])

# -----------------------------
# Configure Gemini
# -----------------------------
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

# -----------------------------
# FastAPI
# -----------------------------
app = FastAPI()

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Request Model
# -----------------------------
class ChatRequest(BaseModel):
    message: str

# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to LawMate AI Backend!"
    }

# -----------------------------
# Chat
# -----------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    response = model.generate_content(request.message)

    return {
        "reply": response.text
    }