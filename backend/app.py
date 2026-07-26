from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# READ GEMINI API KEY
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

print("Loaded API Key ends with:", api_key[-4:])


# ==========================================
# CONFIGURE GEMINI
# ==========================================

client = genai.Client(api_key=api_key)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()


# ==========================================
# ENABLE CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):

    message: str


# ==========================================
# HOME ROUTE
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Welcome to LawMate AI Backend!"
    }


# ==========================================
# CHAT ROUTE
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    print("Received message:", request.message)


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


    print("Sending request to Gemini...")


    response = client.models.generate_content(

        model="gemini-flash-latest",

        contents=prompt,

    )


    print("Gemini response received!")


    return {

        "reply": response.text

    }