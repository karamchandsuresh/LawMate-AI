# LawMate AI

**A Multilingual RAG-Based Legal Intelligence and Document Analysis Platform for India**

LawMate AI is an academic Generative AI project designed to make Indian legal information easier to access and understand. It combines Retrieval-Augmented Generation (RAG), a local legal knowledge base, multilingual processing, document analysis, complaint drafting, case assessment, and hybrid online/local language models in a single web application.

The platform supports **Google Gemini** for online AI processing and **Llama 3.2 3B through Ollama** for local processing. An **Auto** mode can use Gemini when available and fall back to the local model when needed.

> **Disclaimer:** LawMate AI is an educational and informational system. It does not replace a qualified advocate, and its outputs should not be treated as professional legal advice or a guaranteed prediction of a legal outcome.

---

## Key Features

- **RAG-Based Legal Question Answering** — retrieves relevant information from the LawMate legal knowledge base before generating grounded answers.
- **Hybrid AI Modes** — Auto, Gemini Online, and Llama 3.2 3B Local.
- **Multilingual Interaction** — supports English and multiple Indian languages, including Hindi, Malayalam, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Punjabi, and Urdu.
- **Document Analysis** — supports PDF, DOCX, TXT, JPG, JPEG, and PNG, with OCR support for images.
- **Complaint Generator** — creates structured complaint drafts from user-provided information.
- **Case Assessment** — provides a cautious AI-assisted assessment of case facts, evidence, strengths, weaknesses, and possible next steps.
- **Agentic Workflow Routing** — identifies the user's intent and directs specialized requests to the appropriate LawMate feature.
- **Conversation Continuity** — uses recent conversation context for follow-up questions.
- **Persistent Current Chat** — retains the active conversation while navigating between pages.
- **New Chat** — clears the current conversation and starts a fresh session.
- **Legal Grounding and Source References** — RAG answers use retrieved legal context and can display source information from the indexed knowledge base.

---

## Problem Statement

Legal information is often difficult for ordinary users to locate, interpret, and connect to their own situations. General-purpose language models can produce fluent answers, but they may also generate unsupported or inaccurate legal information.

LawMate AI addresses this problem by combining a curated Indian legal knowledge base with Retrieval-Augmented Generation. Relevant legal material is retrieved first and supplied as context before the selected language model generates an answer.

The platform also provides practical workflows for document analysis, complaint drafting, case assessment, multilingual interaction, and local AI processing.

---

## Objectives

1. Provide accessible AI-assisted information about Indian law.
2. Ground legal answers using Retrieval-Augmented Generation.
3. Reduce unsupported legal claims by using retrieved source context.
4. Support multiple Indian languages.
5. Analyze uploaded documents in common formats.
6. Generate structured complaint drafts from user-provided information.
7. Provide cautious, non-deterministic case assessments.
8. Route requests to specialized legal workflows.
9. Support both cloud-based and local language models.
10. Preserve conversational context for natural follow-up questions.

---

## System Architecture

```text
React + Vite Frontend
        |
        v
FastAPI Backend
        |
        +---------------------------+
        |                           |
        v                           v
Agentic / Intent Routing     Multilingual Layer
        |                           |
        +-------------+-------------+
                      |
                      v
               LawMate Services
        +-------------+-------------+
        |             |             |
        v             v             v
   RAG Legal QA   Document      Complaint /
                  Analysis      Case Assessment
        |
        v
Sentence-Transformer Embeddings
        |
        v
ChromaDB Legal Knowledge Base
        |
        v
Hybrid LLM Layer
Gemini Online / Llama 3.2 3B Local
        |
        v
Multilingual User Response
```

---

## RAG Workflow

```text
User Legal Question
        |
        v
Multilingual Input Handling
        |
        v
Conversation Context Resolution
        |
        v
Agentic Intent Classification
        |
        v
Embedding Generation
        |
        v
ChromaDB Similarity Search
        |
        v
Relevant Legal Chunks
        |
        v
Prompt + Retrieved Legal Context
        |
        v
Gemini / Local Llama
        |
        v
Grounded Legal Response
        |
        v
Selected-Language Response
```

### Why RAG?

A standalone LLM generates answers primarily from information learned during training. For a legal-information system, this can lead to unsupported claims or incorrect references.

LawMate uses RAG so that relevant legal material is retrieved first. The language model is then instructed to answer using that supplied context and to acknowledge when the available sources are insufficient.

---

## Agentic Workflow

```text
User Request
     |
     v
Intent Classification
     |
     +-- Legal Question -------> RAG Legal QA
     +-- Complaint Request ----> Complaint Generator
     +-- Case Assessment ------> Case Assessment
     +-- Document Analysis ----> Document Analysis
     +-- Non-Legal Request ----> Scope Guidance
```

The router combines direct routing rules for clear requests with model-assisted classification for more ambiguous requests.

---

## Hybrid AI Architecture

### Auto (Recommended)

Uses the online Gemini path when available and can fall back to Local Llama when required.

### Gemini - Online

Uses Google's Gemini cloud model through the configured API.

### Llama 3.2 3B - Local

Uses **Llama 3.2 3B** through **Ollama** on the local computer. It provides a local alternative to the cloud model and can work without internet when the required local components are available.

The local model does **not** replace RAG. Legal questions can still retrieve context from the same ChromaDB knowledge base before response generation.

---

## Multilingual Workflow

```text
User Input
    |
    v
Language Detection / Selected Language
    |
    v
English Processing Query when required
    |
    v
RAG / Specialized LawMate Service
    |
    v
Gemini or Local Llama
    |
    v
Response Translation
    |
    v
Selected User Language
```

---

## Legal Knowledge Base

The LawMate knowledge pipeline was designed around authoritative Indian legal material, including sources such as:

- India Code
- Supreme Court of India
- Selected High Court material
- Gazette of India
- Law Commission of India

Documents are cleaned, divided into smaller chunks, embedded, and stored in ChromaDB for semantic retrieval.

> The exact contents of a local knowledge-base build depend on the documents processed and indexed for that build.

---

## Document Analysis

Supported inputs include:

- PDF
- DOCX
- TXT
- JPG
- JPEG
- PNG

Text is extracted directly where possible. Images can be processed using OCR through Tesseract. The extracted content is then analyzed by the selected AI provider.

Typical output may include a document overview, summary, important points, parties, potential issues or risks, and areas for further review.

---

## Complaint Generator

The Complaint Generator can use:

- Complaint type
- Problem description
- Complainant details
- Opposite party
- Incident date and location
- Amount involved
- Evidence description
- Desired relief
- Optional supporting files

LawMate uses these details to create a structured complaint draft. User-provided evidence descriptions are treated as unverified unless supported by uploaded material.

---

## Case Assessment

The Case Assessment feature considers information supplied by the user, such as case type, case facts, user role, opposite party, evidence summary, and desired outcome.

It can highlight supporting factors, weaknesses, missing information, and possible next steps.

This feature is an **assessment**, not a guaranteed prediction of whether a case will be won or lost.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | FastAPI, Python |
| Online LLM | Google Gemini |
| Local LLM | Llama 3.2 3B through Ollama |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| PDF Processing | pypdf |
| DOCX Processing | python-docx |
| Image Processing | Pillow |
| OCR | Tesseract / pytesseract |
| API Communication | REST / HTTP |
| Markdown Rendering | react-markdown, remark-gfm |
| Environment Variables | python-dotenv |

---

## Project Structure

```text
LawMate-AI/
|
+-- backend/
|   +-- app.py
|   +-- services/
|   |   +-- llm_service.py
|   |   +-- rag_service.py
|   |   +-- multilingual_service.py
|   |   +-- document_analyzer.py
|   |   +-- complaint_generator.py
|   |   +-- case_predictor.py
|   |
|   +-- data_pipeline/
|   |   +-- raw_data/
|   |   +-- cleaned_data/
|   |   +-- chunking/
|   |   +-- embeddings/
|   |   +-- chroma_db/
|   |   +-- scraper/
|   |
|   +-- requirements.txt
|   +-- .env
|
+-- frontend/
|   +-- src/
|   |   +-- components/
|   |   +-- context/
|   |   |   +-- LanguageContext.jsx
|   |   |   +-- AIModelContext.jsx
|   |   +-- pages/
|   |   |   +-- Home.jsx
|   |   |   +-- Chat.jsx
|   |   |   +-- Upload.jsx
|   |   |   +-- Complaint.jsx
|   |   |   +-- CaseAssessment.jsx
|   |   |   +-- About.jsx
|   |   +-- App.jsx
|   |   +-- main.jsx
|   |
|   +-- package.json
|
+-- .gitignore
+-- README.md
```

Generated data directories may be ignored by Git depending on the project configuration.

---

## Local Installation

### Prerequisites

Install:

- Python
- Node.js and npm
- Git
- Ollama for Local Llama mode
- Tesseract OCR if image OCR is required

### 1. Clone the Repository

```bash
git clone https://github.com/karamchandsuresh/LawMate-AI.git
cd LawMate-AI
```

### 2. Backend Setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` and configure the Gemini API environment variable required by the project.

Start the backend:

```powershell
uvicorn app:app --reload
```

The backend normally runs at `http://127.0.0.1:8000`.

### 3. Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local Vite address displayed in the terminal.

---

## Local Llama Setup

Install Ollama and download the model:

```powershell
ollama pull llama3.2:3b
```

Confirm that it is available:

```powershell
ollama list
```

Optional direct test:

```powershell
ollama run llama3.2:3b
```

After LawMate is running, choose the Local Llama option from the AI Mode selector.

---

## Running LawMate

### Terminal 1 - Backend

```powershell
cd backend
venv\Scripts\activate
uvicorn app:app --reload
```

### Terminal 2 - Frontend

```powershell
cd frontend
npm run dev
```

Ollama must also be available when Local Llama mode is selected.

---

## Limitations

- LawMate is not a substitute for professional legal advice.
- Generated information can still contain errors and should be verified.
- RAG quality depends on the quality and coverage of indexed legal documents.
- Llama 3.2 3B can be slower than the cloud model, particularly on CPU-only systems.
- Smaller local models may provide less detailed output than larger cloud models.
- Multilingual local-model processing can increase response time.
- OCR quality depends on image clarity and Tesseract configuration.
- Case Assessment cannot guarantee real-world court outcomes.
- Current chat persistence is browser-side rather than a full authenticated multi-user conversation database.
- The current version is primarily intended for local execution; cloud deployment was not finalized.

---

## Future Scope

- Production cloud deployment
- User authentication and secure user accounts
- Server-side conversation history
- Multiple saved or named chats
- Larger or optimized local language models
- Faster local inference
- Expanded Indian legal knowledge coverage
- Automated legal-source update pipelines
- Improved citation presentation
- Advanced document comparison
- Speech-based multilingual interaction
- Stronger evaluation using expert-reviewed legal QA datasets
- Improved production privacy and security controls

---

## Responsible AI Considerations

LawMate follows important responsible-AI principles:

- Legal answers should be grounded in available source material.
- The system should state uncertainty when sufficient evidence is unavailable.
- Case Assessment should not claim guaranteed outcomes.
- User-provided allegations and evidence descriptions should not automatically be treated as verified facts.
- Sensitive information should be handled carefully.
- Important AI-generated legal information should be independently verified.

---

## Academic Scope

LawMate AI demonstrates the integration of:

- Generative AI
- Retrieval-Augmented Generation
- Natural Language Processing
- Semantic embeddings
- Vector databases
- Local and cloud LLMs
- Agentic routing
- Multilingual processing
- OCR and document processing
- REST API development
- Full-stack web development

---

## Project Status

| Component | Status |
|---|---|
| Core Application | Completed |
| RAG Knowledge Retrieval | Completed |
| Gemini Integration | Completed |
| Local Llama / Ollama | Completed |
| Multilingual Support | Completed |
| Document Analysis | Completed |
| Complaint Generator | Completed |
| Case Assessment | Completed |
| Agentic Routing | Completed |
| Conversation Continuity | Completed |
| Git / GitHub | Completed |
| Cloud Deployment | Not finalized |

---

## Author

**Karamchand Suresh**  
MCA - Generative AI  
Alliance University, Bengaluru

---

## Usage Note

This repository was developed as an academic project. Before redistributing third-party legal documents, datasets, models, or external-service content, review the applicable licenses, terms of use, and attribution requirements.
