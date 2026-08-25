import os

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

from services.rag_service import rag_query
from services.document_analyzer import (
    process_document,
    extract_text_from_file,
)
from services.complaint_generator import generate_complaint
from services.multilingual_service import (
    prepare_multilingual_query,
    prepare_multilingual_response,
)
from services.case_predictor import assess_case


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
    description=(
        "Backend API for LawMate AI — "
        "Indian legal intelligence, RAG chat, "
        "legal document analysis, and complaint drafting."
    ),
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


class ComplaintRequest(BaseModel):
    complaint_type: str
    problem_description: str
    complainant_name: str = ""
    complainant_address: str = ""
    complainant_contact: str = ""
    opposite_party: str = ""
    incident_date: str = ""
    incident_location: str = ""
    amount_involved: str = ""
    evidence: str = ""
    desired_relief: str = ""


class CaseAssessmentRequest(BaseModel):
    case_type: str
    case_facts: str
    user_role: str = ""
    opposite_party: str = ""
    evidence_summary: str = ""
    desired_outcome: str = ""


# ============================================================
# DOCUMENT ANALYZER CONFIGURATION
# ============================================================

SUPPORTED_DOCUMENT_TYPES = {
    ".pdf",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_DOCUMENT_SIZE = (
    10 * 1024 * 1024
)

# 10 MB maximum upload size for Version 1.


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
    Classify a user message into one LawMate workflow.

    Categories:
    legal_question
    complaint_request
    case_assessment
    document_analysis
    non_legal
    """

    prompt = f"""
You are the workflow intent router for LawMate AI.

Classify the user's message into EXACTLY ONE category:

legal_question
complaint_request
case_assessment
document_analysis
non_legal

Definitions:

legal_question:
The user is asking an ordinary legal question about Indian
law, rights, procedures, Acts, sections, courts, remedies,
consumer issues, employment, family law, criminal law,
civil law, cyber law, property law, or similar topics.

complaint_request:
The user clearly wants LawMate to create, draft, write,
prepare, or generate a complaint.

case_assessment:
The user clearly wants LawMate to assess the strength,
weakness, outlook, or overall position of their case.

document_analysis:
The user wants to upload, review, analyze, explain,
summarize, or check a document, agreement, notice,
PDF, DOCX, image, or similar file.

non_legal:
The request is unrelated to legal assistance.

Important:
If the user is only asking a general legal question that
mentions complaints, cases, or documents, use legal_question
unless they clearly request one of the specialized workflows.

USER MESSAGE:

{message}

Return ONLY one category.
"""

    try:
        response = gemini_client.models.generate_content(
            model=ROUTER_MODEL,
            contents=prompt
        )

        intent = response.text.strip().lower()

        allowed_intents = {
            "legal_question",
            "complaint_request",
            "case_assessment",
            "document_analysis",
            "non_legal",
        }

        if intent in allowed_intents:
            return intent

        return "legal_question"

    except Exception as error:
        print(
            "Intent classification error:",
            error
        )

        return "legal_question"


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
        "document_analyzer": "enabled",
        "complaint_generator": "enabled",
        "multilingual_chat": "enabled",
        "case_assessment": "enabled",
        "supported_documents": [
            "PDF",
            "DOCX",
            "JPG",
            "JPEG",
            "PNG",
        ],
    }


# ============================================================
# CHAT ROUTE
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    original_message = request.message.strip()

    print()
    print("=" * 70)
    print("LAWMATE AI CHAT")
    print("=" * 70)
    print("User:", original_message)

    if not original_message:
        return {
            "reply": "Please enter a question.",
            "mode": "validation",
            "grounded": False,
            "sources": [],
            "language": "english",
        }

    # Detect the user's language and translate the query to
    # English before intent classification and RAG retrieval.
    try:
        multilingual_input = prepare_multilingual_query(
            original_message
        )
        user_language = multilingual_input["language"]
        message = multilingual_input["english_text"]
    except Exception as error:
        print("Multilingual input error:", error)
        user_language = "english"
        message = original_message

    print("Detected language:", user_language)

    if user_language != "english":
        print("English query:", message)

    # Greeting detection is performed on the English form so
    # greetings in supported languages can use the same logic.
    if is_greeting(message):

        english_reply = (
            "Hello! 👋 I'm LawMate AI. "
            "I can help you understand Indian laws, "
            "legal rights, court decisions, complaints, "
            "and other legal matters. "
            "How can I assist you?"
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception as error:
            print("Greeting translation error:", error)
            reply = english_reply

        return {
            "reply": reply,
            "mode": "greeting",
            "grounded": False,
            "sources": [],
            "language": user_language,
        }

    print("Classifying user intent...")

    intent = classify_intent(message)

    print("Intent:", intent)

    if intent == "complaint_request":

        english_reply = (
            "This looks like a complaint-drafting request. "
            "LawMate's Complaint Generator can collect the "
            "required details and prepare a structured draft.\n\n"
            "Would you like to continue to the Complaint Generator?"
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception as error:
            print(
                "Complaint routing translation error:",
                error
            )
            reply = english_reply

        return {
            "reply": reply,
            "mode": "route",
            "grounded": False,
            "sources": [],
            "language": user_language,
            "route": "/complaint",
            "action_label": "Generate Complaint →",
        }


    if intent == "case_assessment":

        english_reply = (
            "This looks like a case-assessment request. "
            "LawMate's Case Assessment tool can review your "
            "facts, evidence, strengths, uncertainties, and "
            "possible next steps.\n\n"
            "Would you like to continue to Case Assessment?"
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception as error:
            print(
                "Case routing translation error:",
                error
            )
            reply = english_reply

        return {
            "reply": reply,
            "mode": "route",
            "grounded": False,
            "sources": [],
            "language": user_language,
            "route": "/case-assessment",
            "action_label": "Assess My Case →",
        }


    if intent == "document_analysis":

        english_reply = (
            "This looks like a document-analysis request. "
            "LawMate's Document Analyzer can process PDF, DOCX, "
            "JPG, JPEG, and PNG files and explain their contents.\n\n"
            "Would you like to continue to Document Analysis?"
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception as error:
            print(
                "Document routing translation error:",
                error
            )
            reply = english_reply

        return {
            "reply": reply,
            "mode": "route",
            "grounded": False,
            "sources": [],
            "language": user_language,
            "route": "/upload",
            "action_label": "Upload & Analyze Document →",
        }


    if intent == "non_legal":

        english_reply = (
            "I'm LawMate AI, designed primarily "
            "for Indian legal assistance. ⚖️\n\n"
            "I can help with laws, legal rights, "
            "court decisions, complaints, contracts, "
            "consumer issues, cyber law, criminal law, "
            "family law, and related legal matters."
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception as error:
            print(
                "Non-legal response translation error:",
                error
            )
            reply = english_reply

        return {
            "reply": reply,
            "mode": "non_legal",
            "grounded": False,
            "sources": [],
            "language": user_language,
        }

    print(
        "Searching verified LawMate RAG sources..."
    )

    try:
        # The existing English legal knowledge base remains
        # unchanged. RAG receives the English query.
        result = rag_query(
            message,
            top_k=3
        )
    except Exception as error:

        print("RAG error:", error)

        english_reply = (
            "LawMate encountered a temporary "
            "problem while processing your legal "
            "question. Please try again."
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception:
            reply = english_reply

        return {
            "reply": reply,
            "mode": "error",
            "grounded": False,
            "sources": [],
            "language": user_language,
        }

    answer = result.get("answer", "")
    sources = result.get("sources", [])

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

            english_reply = (
                "The current LawMate legal "
                "knowledge base does not contain "
                "enough verified information to "
                "answer this question reliably."
            )

            try:
                reply = prepare_multilingual_response(
                    english_reply,
                    user_language
                )
            except Exception:
                reply = english_reply

            return {
                "reply": reply,
                "mode": "insufficient",
                "grounded": False,
                "sources": [],
                "language": user_language,
            }

        english_reply = (
            "🟡 Grounding Status: "
            "General AI Information — "
            "Not verified by LawMate RAG sources\n\n"
            "The current LawMate legal knowledge base "
            "does not contain enough verified "
            "information to answer this question "
            "reliably.\n\n"
            f"{fallback_answer}"
        )

        try:
            reply = prepare_multilingual_response(
                english_reply,
                user_language
            )
        except Exception as error:
            print(
                "Fallback response translation error:",
                error
            )
            reply = english_reply

        return {
            "reply": reply,
            "mode": "gemini_fallback",
            "grounded": False,
            "sources": [],
            "language": user_language,
        }

    citations = format_verified_sources(
        sources
    )

    english_reply = (
        "🟢 Grounding Status: "
        "Verified from LawMate RAG sources\n\n"
        f"{answer}\n\n"
        "📚 Verified LawMate Sources\n\n"
        f"{citations}"
    )

    try:
        reply = prepare_multilingual_response(
            english_reply,
            user_language
        )
    except Exception as error:
        print(
            "RAG response translation error:",
            error
        )
        reply = english_reply

    print(
        "Verified RAG answer generated."
    )

    return {
        "reply": reply,
        "mode": "rag",
        "grounded": True,
        "sources": sources,
        "language": user_language,
    }


# ============================================================
# CASE ASSESSMENT ROUTE
# ============================================================

@app.post("/assess-case")
def assess_case_route(request: CaseAssessmentRequest):
    """
    Provide a cautious qualitative assessment of a
    user-described legal case.

    This endpoint does not predict a guaranteed court result.
    """

    print()
    print("=" * 70)
    print("LAWMATE AI CASE ASSESSMENT")
    print("=" * 70)
    print("Case type:", request.case_type)

    try:
        result = assess_case(
            case_type=request.case_type,
            case_facts=request.case_facts,
            user_role=request.user_role,
            opposite_party=request.opposite_party,
            evidence_summary=request.evidence_summary,
            desired_outcome=request.desired_outcome,
        )

    except ValueError as error:
        print("Case assessment validation error:", error)
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        print("Case assessment error:", error)
        raise HTTPException(
            status_code=500,
            detail=(
                "LawMate encountered an error while "
                "assessing this case."
            ),
        )

    print("Case assessment completed successfully.")

    return {
        "status": "success",
        "mode": "case_assessment",
        "case_type": result["case_type"],
        "assessment": result["assessment"],
        "prediction_notice": (
            "This is a qualitative case assessment based "
            "only on the information supplied by the user. "
            "It does not predict or guarantee a court outcome."
        ),
    }


# ============================================================
# DOCUMENT ANALYZER ROUTE
# ============================================================

@app.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...)
):
    """
    Analyze an uploaded legal document.

    Supported:
    PDF
    DOCX
    JPG
    JPEG
    PNG
    """

    print()
    print("=" * 70)
    print("LAWMATE AI DOCUMENT ANALYZER")
    print("=" * 70)


    # ========================================================
    # VALIDATE FILE NAME
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file does not "
                "have a valid filename."
            ),
        )


    filename = file.filename.strip()

    print(
        "Uploaded file:",
        filename
    )


    # ========================================================
    # VALIDATE FILE EXTENSION
    # ========================================================

    extension = os.path.splitext(
        filename.lower()
    )[1]

    if extension not in SUPPORTED_DOCUMENT_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload PDF, DOCX, "
                "JPG, JPEG, or PNG."
            ),
        )


    # ========================================================
    # READ UPLOADED FILE
    # ========================================================

    try:

        file_bytes = await file.read()

    except Exception as error:

        print(
            "File read error:",
            error
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to read the uploaded file."
            ),
        )


    # ========================================================
    # EMPTY FILE CHECK
    # ========================================================

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file is empty."
            ),
        )


    # ========================================================
    # FILE SIZE CHECK
    # ========================================================

    if len(file_bytes) > MAX_DOCUMENT_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "The uploaded file is too large. "
                "Maximum supported size is 10 MB."
            ),
        )


    print(
        f"File size: "
        f"{len(file_bytes):,} bytes"
    )


    # ========================================================
    # PROCESS DOCUMENT
    # ========================================================

    try:

        result = process_document(
            filename,
            file_bytes
        )

    except ValueError as error:

        print(
            "Document validation error:",
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:

        print(
            "Document processing error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:

        print(
            "Unexpected document analyzer error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "LawMate encountered an error "
                "while analyzing this document."
            ),
        )


    # ========================================================
    # SUCCESS
    # ========================================================

    print(
        "Document analysis completed successfully."
    )

    print(
        "Characters extracted:",
        result.get(
            "characters_extracted",
            0
        )
    )


    return {
        "status": "success",
        "mode": "document_analysis",
        "filename": result[
            "filename"
        ],
        "characters_extracted": result[
            "characters_extracted"
        ],
        "analysis": result[
            "analysis"
        ],
        "supported_formats": [
            "PDF",
            "DOCX",
            "JPG",
            "JPEG",
            "PNG",
        ],
    }

# ============================================================
# COMPLAINT GENERATOR ROUTE
# ============================================================
# ============================================================
# COMPLAINT GENERATOR ROUTE
# ============================================================

MAX_EVIDENCE_FILES = 5
MAX_EVIDENCE_FILE_SIZE = 10 * 1024 * 1024


def classify_evidence_relevance(
    complaint_type,
    problem_description,
    filename,
    extracted_text,
):
    """
    Assess apparent relevance only.
    This does not authenticate evidence.
    """

    if not extracted_text.strip():
        return {
            "filename": filename,
            "relevance": "possibly relevant",
            "reason": (
                "No readable text could be extracted "
                "from this file."
            ),
            "recommendation": (
                "Review this file manually before "
                "deciding whether to attach it."
            ),
            "status": (
                "Possibly Relevant — manual review recommended"
            ),
        }

    prompt = f"""
You are LawMate AI.

Assess ONLY whether this USER-SUPPLIED file appears relevant
 to the complaint below.

This is NOT an authenticity or admissibility check.
Never claim that the file is genuine, original, unedited,
verified, legally admissible, or conclusive.

COMPLAINT TYPE:
{complaint_type}

PROBLEM DESCRIPTION:
{problem_description}

UPLOADED FILE:
{filename}

EXTRACTED TEXT:
{extracted_text[:12000]}

Classify the file as exactly one of:
relevant
possibly relevant
irrelevant

Relevant means the readable contents directly relate to the
facts, transaction, communication, parties, incident, loss,
or relief in the complaint.

Possibly relevant means the connection is incomplete,
unclear, indirect, or there is not enough readable content.

Irrelevant means the readable contents appear unrelated to
the stated complaint.

If relevant, recommend attaching it after user review.
If possibly relevant, recommend reviewing it before attachment.
If irrelevant, recommend not attaching it unless the user can
explain a real connection.

Return EXACTLY three lines:
RELEVANCE: relevant OR possibly relevant OR irrelevant
REASON: one short sentence
RECOMMENDATION: one short sentence
"""

    try:
        response = gemini_client.models.generate_content(
            model=ROUTER_MODEL,
            contents=prompt,
        )

        relevance = "possibly relevant"
        reason = (
            "LawMate could not determine relevance "
            "with high confidence."
        )
        recommendation = (
            "Review this file manually before deciding "
            "whether to attach it."
        )

        for line in response.text.splitlines():
            cleaned = line.strip()
            lower = cleaned.lower()

            if lower.startswith("relevance:"):
                value = cleaned.split(":", 1)[1].strip().lower()
                if value in {
                    "relevant",
                    "possibly relevant",
                    "irrelevant",
                }:
                    relevance = value

            elif lower.startswith("reason:"):
                value = cleaned.split(":", 1)[1].strip()
                if value:
                    reason = value

            elif lower.startswith("recommendation:"):
                value = cleaned.split(":", 1)[1].strip()
                if value:
                    recommendation = value

    except Exception as error:
        print("Evidence relevance analysis error:", error)

        relevance = "possibly relevant"
        reason = (
            "Automatic relevance assessment was unavailable."
        )
        recommendation = (
            "Review this file manually before deciding "
            "whether to attach it."
        )

    relevance_label = relevance.title()

    return {
        "filename": filename,
        "relevance": relevance,
        "reason": reason,
        "recommendation": recommendation,
        "status": (
            f"{relevance_label} — {recommendation}"
        ),
    }


@app.post("/generate-complaint")
async def generate_complaint_route(
    complaint_type: str = Form(...),
    problem_description: str = Form(...),
    complainant_name: str = Form(""),
    complainant_address: str = Form(""),
    complainant_contact: str = Form(""),
    opposite_party: str = Form(""),
    incident_date: str = Form(""),
    incident_location: str = Form(""),
    amount_involved: str = Form(""),
    evidence: str = Form(""),
    desired_relief: str = Form(""),
    evidence_files: list[UploadFile] | None = File(None),
):
    """
    Generate a complaint from user-provided facts and optional
    uploaded supporting material.
    """

    print()
    print("=" * 70)
    print("LAWMATE AI COMPLAINT GENERATOR")
    print("=" * 70)

    complaint_type = complaint_type.strip()
    problem_description = problem_description.strip()
    complainant_name = complainant_name.strip()
    complainant_address = complainant_address.strip()
    complainant_contact = complainant_contact.strip()
    opposite_party = opposite_party.strip()
    incident_date = incident_date.strip()
    incident_location = incident_location.strip()
    amount_involved = amount_involved.strip()
    evidence = evidence.strip()
    desired_relief = desired_relief.strip()

    print("Complaint type:", complaint_type)

    uploaded_files = [
        file
        for file in (evidence_files or [])
        if file and file.filename
    ]

    if len(uploaded_files) > MAX_EVIDENCE_FILES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Please upload no more than "
                f"{MAX_EVIDENCE_FILES} evidence files."
            ),
        )

    evidence_results = []
    evidence_text_blocks = []
    evidence_filenames = []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.filename.strip()
        extension = os.path.splitext(filename.lower())[1]

        if extension not in SUPPORTED_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported evidence file: {filename}. "
                    "Supported formats are PDF, DOCX, JPG, "
                    "JPEG, and PNG."
                ),
            )

        try:
            file_bytes = await uploaded_file.read()
        except Exception as error:
            print("Evidence file read error:", error)
            raise HTTPException(
                status_code=400,
                detail=f"Unable to read evidence file: {filename}.",
            )

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Evidence file is empty: {filename}.",
            )

        if len(file_bytes) > MAX_EVIDENCE_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Evidence file is too large: {filename}. "
                    "Maximum size is 10 MB."
                ),
            )

        try:
            extracted_text = extract_text_from_file(
                filename,
                file_bytes,
            )
        except RuntimeError as error:
            raise HTTPException(
                status_code=500,
                detail=str(error),
            )
        except Exception as error:
            print("Evidence extraction warning:", filename, error)
            extracted_text = ""

        extracted_text = extracted_text.strip()
        evidence_filenames.append(filename)

        relevance = classify_evidence_relevance(
            complaint_type=complaint_type,
            problem_description=problem_description,
            filename=filename,
            extracted_text=extracted_text,
        )

        relevance["characters_extracted"] = len(extracted_text)
        evidence_results.append(relevance)

        evidence_text_blocks.append(
            (
                f"FILE: {filename}\n"
                f"RELEVANCE: {relevance['relevance']}\n"
                f"REASON: {relevance['reason']}\n"
                f"ATTACHMENT RECOMMENDATION: "
                f"{relevance['recommendation']}\n"
                f"EXTRACTED USER-SUPPLIED CONTENT:\n"
                f"{extracted_text[:12000] if extracted_text else '[No readable text extracted]'}"
            )
        )

    uploaded_evidence_text = "\n\n".join(evidence_text_blocks)

    try:
        result = generate_complaint(
            complaint_type=complaint_type,
            problem_description=problem_description,
            complainant_name=complainant_name,
            complainant_address=complainant_address,
            complainant_contact=complainant_contact,
            opposite_party=opposite_party,
            incident_date=incident_date,
            incident_location=incident_location,
            amount_involved=amount_involved,
            evidence=evidence,
            desired_relief=desired_relief,
            uploaded_evidence_text=uploaded_evidence_text,
            uploaded_evidence_files=evidence_filenames,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print("Complaint generation error:", error)
        raise HTTPException(
            status_code=500,
            detail=(
                "LawMate encountered an error "
                "while generating the complaint."
            ),
        )

    print("Complaint generated successfully.")

    return {
        "status": "success",
        "mode": "complaint_generation",
        "complaint_type": result["complaint_type"],
        "complaint_label": result["complaint_label"],
        "draft": result["draft"],
        "evidence_files": evidence_results,
        "evidence_notice": (
            "LawMate assesses only apparent relevance of "
            "user-supplied material. It does not verify "
            "authenticity, originality, editing history, "
            "completeness, or legal admissibility."
        ),
    }
