import os
import chromadb

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please add it to backend/.env"
    )


# ============================================================
# INITIALIZE GEMINI
# ============================================================

print("Connecting to Gemini...")

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

print("Gemini connected.")


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "data_pipeline",
    "chroma_db"
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print(
    "Embedding model loaded successfully."
)


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("Connecting to ChromaDB...")

chroma_client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = chroma_client.get_collection(
    name="legal_documents"
)

print("ChromaDB connected.")

print(
    f"Documents available: "
    f"{collection.count()}"
)


# ============================================================
# RETRIEVE LEGAL DOCUMENTS
# ============================================================

def retrieve_documents(
    query,
    top_k=3
):
    """
    Convert the user question into an embedding
    and retrieve the most relevant legal chunks
    from ChromaDB.
    """

    # Convert question to embedding
    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = (
        results["documents"][0]
        if results["documents"]
        else []
    )

    distances = (
        results["distances"][0]
        if results["distances"]
        else []
    )

    metadatas = (
        results["metadatas"][0]
        if results["metadatas"]
        else []
    )

    ids = (
        results["ids"][0]
        if results["ids"]
        else []
    )

    return (
        documents,
        distances,
        ids,
        metadatas
    )


# ============================================================
# BUILD LEGAL CONTEXT
# ============================================================

def build_context(
    documents,
    ids,
    metadatas
):
    """
    Build structured legal context for Gemini.

    Each retrieved chunk includes source information
    so Gemini can provide meaningful references.
    """

    context_parts = []

    for index, (
        document,
        document_id,
        metadata
    ) in enumerate(
        zip(
            documents,
            ids,
            metadatas
        ),
        start=1
    ):

        source_type = metadata.get(
            "source_type",
            "unknown"
        )

        source_file = metadata.get(
            "source_file",
            "unknown"
        )

        source_chunk = metadata.get(
            "source_chunk",
            "unknown"
        )

        context_part = f"""
SOURCE {index}

Database ID:
{document_id}

Source Type:
{source_type}

Source Document:
{source_file}

Source Chunk:
{source_chunk}

Legal Text:
{document}
"""

        context_parts.append(
            context_part.strip()
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# GENERATE LEGAL ANSWER
# ============================================================

def generate_answer(
    question,
    context
):
    """
    Generate a grounded legal answer using
    only retrieved legal context.
    """

    prompt = f"""
You are LawMate AI, an AI-powered legal information
assistant focused on Indian law.

You must answer the user's question using ONLY the
legal context provided below.

IMPORTANT RULES:

1. Do not invent legal facts.

2. Do not invent:
   - Acts
   - sections
   - penalties
   - cases
   - judgments
   - dates
   - legal conclusions

3. If the retrieved context does not contain enough
   information, clearly say:

   "The available legal sources do not contain enough
   information to answer this question."

4. Explain the answer using simple and understandable
   language.

5. Use headings and bullet points where appropriate.

6. Mention the actual legal source document used.

7. Do not use only internal chunk IDs as citations.

8. Use source names such as:

   India Code — Bharatiya Nyaya Sanhita, 2023

   whenever that information exists in the context.

9. Mention relevant sections only when the retrieved
   legal text clearly supports them.

10. Do not claim to be a lawyer.

11. State that the information is educational and
    does not replace professional legal advice.

============================================================
LEGAL CONTEXT
============================================================

{context}

============================================================
USER QUESTION
============================================================

{question}

============================================================
ANSWER FORMAT
============================================================

⚖️ Summary

Provide a direct and simple answer.

📌 Key Legal Points

Use short bullet points.

📚 Legal References

Mention the source documents actually used.

⚠️ Disclaimer

State briefly that this is legal information and not
professional legal advice.
"""

    response = (
        gemini_client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
    )

    return response.text


# ============================================================
# FORMAT SOURCES
# ============================================================

def format_sources(
    ids,
    metadatas,
    distances
):
    """
    Create clean source information that can later
    be returned to FastAPI and displayed in React.
    """

    sources = []

    for (
        document_id,
        metadata,
        distance
    ) in zip(
        ids,
        metadatas,
        distances
    ):

        sources.append(
            {
                "id": document_id,

                "source_type": metadata.get(
                    "source_type",
                    "unknown"
                ),

                "source_file": metadata.get(
                    "source_file",
                    "unknown"
                ),

                "source_chunk": metadata.get(
                    "source_chunk",
                    "unknown"
                ),

                "distance": distance
            }
        )

    return sources


# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def rag_query(
    question,
    top_k=3
):
    """
    Complete LawMate AI RAG pipeline.

    Question
        ↓
    Question embedding
        ↓
    ChromaDB retrieval
        ↓
    Source-aware legal context
        ↓
    Gemini
        ↓
    Grounded answer + references
    """

    # --------------------------------------------------------
    # STEP 1 — RETRIEVE
    # --------------------------------------------------------

    (
        documents,
        distances,
        ids,
        metadatas
    ) = retrieve_documents(
        question,
        top_k=top_k
    )

    # --------------------------------------------------------
    # STEP 2 — VALIDATE RETRIEVAL
    # --------------------------------------------------------

    if not documents:

        return {
            "question": question,

            "answer": (
                "No relevant legal documents "
                "were found in the current "
                "LawMate AI knowledge base."
            ),

            "sources": []
        }

    # --------------------------------------------------------
    # STEP 3 — BUILD CONTEXT
    # --------------------------------------------------------

    context = build_context(
        documents,
        ids,
        metadatas
    )

    # --------------------------------------------------------
    # STEP 4 — GENERATE ANSWER
    # --------------------------------------------------------

    answer = generate_answer(
        question,
        context
    )

    # --------------------------------------------------------
    # STEP 5 — FORMAT SOURCES
    # --------------------------------------------------------

    sources = format_sources(
        ids,
        metadatas,
        distances
    )

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    question = (
        "What is the Bharatiya Nyaya "
        "Sanhita, 2023?"
    )

    print()
    print("=" * 70)
    print("USER QUESTION")
    print("=" * 70)

    print(question)

    print()
    print("Running RAG retrieval...")

    result = rag_query(
        question,
        top_k=3
    )

    print()
    print("=" * 70)
    print("GENERATED LEGAL ANSWER")
    print("=" * 70)

    print(
        result["answer"]
    )

    print()
    print("=" * 70)
    print("RETRIEVED SOURCES")
    print("=" * 70)

    for index, source in enumerate(
        result["sources"],
        start=1
    ):

        print()
        print(
            f"Source {index}"
        )

        print(
            f"ID: "
            f"{source['id']}"
        )

        print(
            f"Source Type: "
            f"{source['source_type']}"
        )

        print(
            f"Source File: "
            f"{source['source_file']}"
        )

        print(
            f"Source Chunk: "
            f"{source['source_chunk']}"
        )

        print(
            f"Distance: "
            f"{source['distance']}"
        )