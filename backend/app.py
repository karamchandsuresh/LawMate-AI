from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os

# -----------------------------
# Load Environment Variables
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
client = genai.Client(api_key=api_key)

# -----------------------------
# FastAPI App
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
# Home Route
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to LawMate AI Backend!"
    }

# -----------------------------
# Chat Route
# -----------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    prompt = f"""
You are LawMate AI, an intelligent legal assistant specializing in Indian law.

Always answer using the following format.

⚖️ Summary

Provide a short explanation in 2–3 sentences.

📌 Key Points

• Use bullet points.

• Keep each point short.

• Explain in simple English.

📚 Legal References

Mention relevant:

- Articles of the Constitution
- Acts
- Landmark Supreme Court cases

Important Rules:

- Never return one huge paragraph.
- Always use headings.
- Always use bullet points where appropriate.
- Keep the answer easy to read.
- Focus on Indian law unless the user specifically asks about another country.

User Question:

{request.message}
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
    )

    return {
        "reply": response.text
    }