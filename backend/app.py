import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

from services.rag_service import rag_query


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in backend/.env"
    )


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

# This model already worked successfully with your API key.
ROUTER_MODEL = "gemini-3.1-flash-lite"

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="LawMate AI API",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

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


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# LOCAL GREETING CHECK
# ============================================================

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "hello there",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "hi how are you",
    "hello how are you",
    "thanks",
    "thank you",
}


def normalize_message(message):
    """
    Normalize message for simple greeting detection.
    """

    return " ".join(
        message.lower().strip().split()
    )


def is_greeting(message):
    """
    Detect common conversational greetings locally.

    We do this without Gemini because greetings do not
    require an AI API call.
    """

    normalized = normalize_message(
        message
    )

    if normalized in GREETINGS:
        return True

    greeting_starts = [
        "hi ",
        "hello ",
        "hey ",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if (
        any(
            normalized.startswith(start)
            for start in greeting_starts
        )
        and len(normalized.split()) <= 6
    ):
        return True

    return False


# ============================================================
# INTENT CLASSIFIER
# ============================================================

def classify_intent(message):
    """
    Classify a user message as:

    legal
    non_legal

    Greetings are detected before reaching this function.
    """

    prompt = f"""
You are an intent classifier for LawMate AI.

LawMate AI is an Indian legal information assistant.

Classify the user's message into EXACTLY ONE category:

legal
non_legal

LEGAL includes questions about:

- Indian laws
- Acts
- sections
- legal rights
- Constitution
- criminal matters
- civil matters
- contracts
- property
- employment rights
- consumer disputes
- cyber law
- privacy
- family law
- marriage
- divorce
- maintenance
- domestic violence
- police
- FIR
- bail
- arrest
- courts
- judgments
- legal remedies
- complaints
- legal procedures
- situations where the user may have a legal problem

A question can be legal even if it does NOT explicitly
contain words such as "law", "legal", "court", or "Act".

Examples:

"What is Bharatiya Nyaya Sanhita?"
legal

"Can my landlord remove me without notice?"
legal

"My employer has not paid my salary. What can I do?"
legal

"Someone posted my photo online without permission."
legal

"Who is the best football player?"
non_legal

"How do I cook pasta?"
non_legal

"What is Python?"
non_legal

USER MESSAGE:

{message}

Return ONLY:

legal

or

non_legal
"""

    try:

        response = (
            gemini_client.models.generate_content(
                model=ROUTER_MODEL,
                contents=prompt
            )
        )

        intent = (
            response.text
            .strip()
            .lower()
        )

        if intent == "legal":
            return "legal"

        if intent == "non_legal":
            return "non_legal"

        # Safe fallback
        return "legal"

    except Exception as error:

        print(
            "Intent classification error:",
            error
        )

        # If classification fails, allow RAG to try rather
        # than incorrectly rejecting a legal question.
        return "legal"


# ============================================================
# GEMINI GENERAL LEGAL FALLBACK
# ============================================================

def generate_general_legal_answer(
    question
):
    """
    Generate a cautious legal answer when LawMate's
    verified RAG sources are insufficient.
    """

    prompt = f"""
You are LawMate AI, an Indian legal information assistant.

The LawMate RAG knowledge base did not contain enough
verified information to answer this legal question reliably.

Provide a cautious GENERAL explanation based on your
general knowledge.

IMPORTANT RULES:

1. Focus on Indian law.

2. Clearly state that this information is NOT verified
   against LawMate's RAG knowledge base.

3. Never pretend that general AI knowledge is a verified
   LawMate source.

4. Do not invent court cases.

5. Do not invent legal sections, penalties, or dates if
   you are uncertain.

6. Keep the explanation simple.

7. Recommend verification using an official legal source
   or qualified legal professional where appropriate.

USER QUESTION:

{question}

Use this format:

⚖️ General Legal Information

Provide the explanation.

⚠️ Verification Notice

Explain that this information is based on general AI
knowledge and has not been verified against LawMate's
RAG sources.
"""

    response = (
        gemini_client.models.generate_content(
            model=ROUTER_MODEL,
            contents=prompt
        )
    )

    return response.text


# ============================================================
# FORMAT LAWMATE CITATIONS
# ============================================================

def format_verified_sources(
    sources
):
    """
    Format ChromaDB source metadata as:

    [L1]
    [L2]
    [L3]

    L = LawMate verified source.
    """

    citation_lines = []

    seen = set()

    citation_number = 1

    for source in sources:

        source_type = source.get(
            "source_type",
            "Unknown Source"
        )

        source_file = source.get(
            "source_file",
            "Unknown Document"
        )

        source_chunk = source.get(
            "source_chunk",
            "Unknown"
        )

        citation_key = (
            source_type,
            source_file,
            source_chunk
        )

        if citation_key in seen:
            continue

        seen.add(
            citation_key
        )

        citation_lines.append(
            f"[L{citation_number}] "
            f"{source_type} — "
            f"{source_file} "
            f"(Chunk {source_chunk})"
        )

        citation_number += 1

    return "\n".join(
        citation_lines
    )


# ============================================================
# CHECK RAG SUFFICIENCY
# ============================================================

def rag_is_insufficient(
    answer,
    sources
):
    """
    Detect when RAG itself says that available
    verified context is insufficient.
    """

    if not sources:
        return True

    answer_lower = answer.lower()

    insufficient_phrases = [
        "available legal sources do not contain enough",
        "do not contain enough information",
        "insufficient information",
        "no relevant legal documents",
        "not enough information",
    ]

    return any(
        phrase in answer_lower
        for phrase in insufficient_phrases
    )


# ============================================================
# HOME ROUTE
# ============================================================

@app.get("/")
def home():

    return {
        "message": (
            "Welcome to LawMate AI Backend!"
        ),
        "status": "running",
        "rag": "enabled",
        "router": "enabled",
    }


# ============================================================
# CHAT ROUTE
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    message = request.message.strip()

    print()
    print("=" * 70)
    print("LAWMATE AI CHAT")
    print("=" * 70)

    print(
        "User:",
        message
    )


    # ========================================================
    # EMPTY MESSAGE
    # ========================================================

    if not message:

        return {
            "reply": (
                "Please enter a question."
            ),
            "mode": "validation",
            "grounded": False,
            "sources": [],
        }


    # ========================================================
    # GREETING
    # ========================================================

    if is_greeting(
        message
    ):

        return {
            "reply": (
                "Hello! 👋 I'm LawMate AI. "
                "I can help you understand Indian laws, "
                "legal rights, court decisions, complaints, "
                "and other legal matters. "
                "How can I assist you?"
            ),
            "mode": "greeting",
            "grounded": False,
            "sources": [],
        }


    # ========================================================
    # INTENT CLASSIFICATION
    # ========================================================

    print(
        "Classifying user intent..."
    )

    intent = classify_intent(
        message
    )

    print(
        "Intent:",
        intent
    )


    # ========================================================
    # NON-LEGAL QUESTION
    # ========================================================

    if intent == "non_legal":

        return {
            "reply": (
                "I'm LawMate AI, designed primarily "
                "for Indian legal assistance. ⚖️\n\n"
                "I can help with laws, legal rights, "
                "court decisions, complaints, contracts, "
                "consumer issues, cyber law, criminal law, "
                "family law, and related legal matters."
            ),
            "mode": "non_legal",
            "grounded": False,
            "sources": [],
        }


    # ========================================================
    # LEGAL QUESTION → RAG
    # ========================================================

    print(
        "Searching verified LawMate RAG sources..."
    )

    try:

        result = rag_query(
            message,
            top_k=3
        )

    except Exception as error:

        print(
            "RAG error:",
            error
        )

        return {
            "reply": (
                "LawMate encountered a temporary "
                "problem while processing your legal "
                "question. Please try again."
            ),
            "mode": "error",
            "grounded": False,
            "sources": [],
        }


    answer = result.get(
        "answer",
        ""
    )

    sources = result.get(
        "sources",
        []
    )


    # ========================================================
    # RAG INSUFFICIENT → GEMINI FALLBACK
    # ========================================================

    if rag_is_insufficient(
        answer,
        sources
    ):

        print(
            "Verified RAG context insufficient."
        )

        print(
            "Using Gemini legal fallback..."
        )

        try:

            fallback_answer = (
                generate_general_legal_answer(
                    message
                )
            )

        except Exception as error:

            print(
                "Gemini fallback error:",
                error
            )

            return {
                "reply": (
                    "The current LawMate legal "
                    "knowledge base does not contain "
                    "enough verified information to "
                    "answer this question reliably."
                ),
                "mode": "insufficient",
                "grounded": False,
                "sources": [],
            }


        reply = (
            "🟡 Grounding Status: "
            "General AI Information — "
            "Not verified by LawMate RAG sources\n\n"
            "The current LawMate legal knowledge base "
            "does not contain enough verified "
            "information to answer this question "
            "reliably.\n\n"
            f"{fallback_answer}"
        )


        return {
            "reply": reply,
            "mode": "gemini_fallback",
            "grounded": False,
            "sources": [],
        }


    # ========================================================
    # VERIFIED RAG ANSWER
    # ========================================================

    citations = (
        format_verified_sources(
            sources
        )
    )


    reply = (
        "🟢 Grounding Status: "
        "Verified from LawMate RAG sources\n\n"
        f"{answer}\n\n"
        "📚 Verified LawMate Sources\n\n"
        f"{citations}"
    )


    print(
        "Verified RAG answer generated."
    )


    return {
        "reply": reply,
        "mode": "rag",
        "grounded": True,
        "sources": sources,
    }