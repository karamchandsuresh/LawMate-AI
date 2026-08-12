import os
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please add it to backend/.env"
    )


# --------------------------------------------------
# INITIALIZE GEMINI
# --------------------------------------------------

print("Connecting to Gemini...")

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

print("Gemini connected.")


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "data_pipeline",
    "chroma_db"
)


# --------------------------------------------------
# LOAD EMBEDDING MODEL
# --------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")


# --------------------------------------------------
# CONNECT TO CHROMADB
# --------------------------------------------------

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name="legal_documents"
)

print("ChromaDB connected.")
print(f"Documents available: {collection.count()}")


# --------------------------------------------------
# RETRIEVE LEGAL DOCUMENTS
# --------------------------------------------------

def retrieve_documents(query, top_k=3):

    # Convert user question into embedding
    query_embedding = model.encode(
        [query]
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    return documents, distances, ids


# --------------------------------------------------
# BUILD LEGAL CONTEXT
# --------------------------------------------------

def build_context(documents, ids):

    context_parts = []

    for i, (doc, doc_id) in enumerate(
        zip(documents, ids),
        start=1
    ):

        context_parts.append(
            f"SOURCE {i} ({doc_id}):\n{doc}"
        )

    return "\n\n".join(context_parts)


# --------------------------------------------------
# GENERATE LEGAL ANSWER
# --------------------------------------------------

def generate_answer(question, context):

    prompt = f"""
You are LawMate AI, an AI legal information assistant
focused on Indian law.

Answer the user's question using ONLY the legal context
provided below.

IMPORTANT RULES:

1. Do not invent legal facts.
2. Do not invent sections, laws, cases, dates, or penalties.
3. If the provided context is insufficient, clearly say so.
4. Explain the answer in simple and understandable language.
5. Mention the relevant source IDs used for the answer.
6. Do not claim to be a lawyer.
7. This is legal information, not professional legal advice.

## LEGAL CONTEXT:

{context}

## USER QUESTION:

{question}

Provide a clear and concise answer.
"""

    response = gemini_client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text


# --------------------------------------------------
# COMPLETE RAG PIPELINE
# --------------------------------------------------

def rag_query(question, top_k=3):

    # Step 1: Retrieve documents
    documents, distances, ids = retrieve_documents(
        question,
        top_k=top_k
    )

    # Step 2: Build context
    context = build_context(
        documents,
        ids
    )

    # Step 3: Generate answer
    answer = generate_answer(
        question,
        context
    )

    return {
        "question": question,
        "answer": answer,
        "sources": ids,
        "distances": distances
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    question = "What is the Aadhaar Act, 2016?"

    print("\n" + "=" * 70)
    print("USER QUESTION")
    print("=" * 70)

    print(question)

    result = rag_query(
        question,
        top_k=3
    )

    print("\n" + "=" * 70)
    print("GENERATED LEGAL ANSWER")
    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES USED")
    print("=" * 70)

    for source in result["sources"]:
        print(source)