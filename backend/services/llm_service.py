import os

import requests
from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# MODEL CONFIGURATION
# ============================================================

GEMINI_MODEL = "gemini-3.1-flash-lite"

OLLAMA_MODEL = "llama3.2:3b"

OLLAMA_GENERATE_URL = (
    "http://127.0.0.1:11434/api/generate"
)

SUPPORTED_LLM_MODES = {
    "auto",
    "gemini",
    "llama",
}


# ============================================================
# MODE NORMALIZATION
# ============================================================

def normalize_llm_mode(mode):
    """
    Normalize the requested LawMate AI model mode.

    Supported modes:

    auto
        Try Gemini first. If Gemini is unavailable,
        automatically fall back to local Llama.

    gemini
        Use Gemini only.

    llama
        Use local Llama through Ollama only.
    """

    if mode is None:
        return "auto"

    normalized_mode = str(mode).strip().lower()

    aliases = {
        "automatic": "auto",
        "recommended": "auto",
        "online": "gemini",
        "google": "gemini",
        "local": "llama",
        "ollama": "llama",
        "llama3.2": "llama",
        "llama3.2:3b": "llama",
    }

    normalized_mode = aliases.get(
        normalized_mode,
        normalized_mode,
    )

    if normalized_mode not in SUPPORTED_LLM_MODES:
        raise ValueError(
            "Unsupported AI model mode. "
            "Choose auto, gemini, or llama."
        )

    return normalized_mode


# ============================================================
# GEMINI
# ============================================================

def generate_with_gemini(prompt):
    """
    Generate a response using Gemini.

    Gemini is initialized only when this function is called.
    This allows LawMate's local Llama mode to work without
    requiring Gemini during application startup.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Gemini is unavailable because "
            "GEMINI_API_KEY is not configured."
        )

    try:
        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        response_text = getattr(
            response,
            "text",
            None,
        )

        if not response_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response_text.strip()

    except Exception as error:
        raise RuntimeError(
            f"Gemini request failed: {error}"
        ) from error


# ============================================================
# OLLAMA / LOCAL LLAMA
# ============================================================

def generate_with_llama(prompt):
    """
    Generate a response locally using Ollama and
    Llama 3.2 3B.

    Internet access is not required after Ollama and
    the model have already been installed locally.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=180,
        )

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "Local Llama is unavailable. "
            "Make sure Ollama is installed and running."
        ) from error

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "Local Llama took too long to respond."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error

    if not response.ok:
        raise RuntimeError(
            "Ollama returned an error "
            f"({response.status_code}): "
            f"{response.text}"
        )

    try:
        data = response.json()

    except ValueError as error:
        raise RuntimeError(
            "Ollama returned an invalid response."
        ) from error

    response_text = data.get(
        "response",
        ""
    ).strip()

    if not response_text:
        raise RuntimeError(
            "Local Llama returned an empty response."
        )

    return response_text


# ============================================================
# COMMON LAWMATE LLM PROVIDER
# ============================================================

def generate_ai_response(
    prompt,
    mode="auto",
):
    """
    Generate an AI response using the selected LawMate mode.

    Returns:

    {
        "text": "...",
        "provider": "gemini" or "llama",
        "requested_mode": "auto" / "gemini" / "llama",
        "fallback_used": True / False
    }
    """

    if not prompt or not str(prompt).strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    normalized_mode = normalize_llm_mode(
        mode
    )

    # --------------------------------------------------------
    # GEMINI ONLY
    # --------------------------------------------------------

    if normalized_mode == "gemini":

        text = generate_with_gemini(
            prompt
        )

        return {
            "text": text,
            "provider": "gemini",
            "requested_mode": "gemini",
            "fallback_used": False,
        }

    # --------------------------------------------------------
    # LLAMA ONLY
    # --------------------------------------------------------

    if normalized_mode == "llama":

        text = generate_with_llama(
            prompt
        )

        return {
            "text": text,
            "provider": "llama",
            "requested_mode": "llama",
            "fallback_used": False,
        }

    # --------------------------------------------------------
    # AUTO
    # --------------------------------------------------------

    try:

        text = generate_with_gemini(
            prompt
        )

        return {
            "text": text,
            "provider": "gemini",
            "requested_mode": "auto",
            "fallback_used": False,
        }

    except Exception as gemini_error:

        print(
            "\n"
            "============================================================"
        )
        print(
            "LAWMATE AI AUTO MODE"
        )
        print(
            "============================================================"
        )
        print(
            "Gemini unavailable."
        )
        print(
            f"Reason: {gemini_error}"
        )
        print(
            "Attempting local Llama fallback..."
        )

        try:

            text = generate_with_llama(
                prompt
            )

            print(
                "Local Llama fallback successful."
            )

            return {
                "text": text,
                "provider": "llama",
                "requested_mode": "auto",
                "fallback_used": True,
            }

        except Exception as llama_error:

            raise RuntimeError(
                "No AI model is currently available. "
                f"Gemini error: {gemini_error} "
                f"Local Llama error: {llama_error}"
            ) from llama_error


# ============================================================
# PROVIDER INFORMATION
# ============================================================

def get_llm_mode_info():
    """
    Return information that can later be displayed
    in the LawMate frontend.
    """

    return {
        "auto": {
            "label": "Auto (Recommended)",
            "description": (
                "Uses Gemini when available and automatically "
                "switches to Local Llama when the online model "
                "is unavailable."
            ),
        },
        "gemini": {
            "label": "Gemini - Online",
            "description": (
                "Uses Google's Gemini cloud model. "
                "Internet and API access are required."
            ),
        },
        "llama": {
            "label": "Llama 3.2 3B - Local",
            "description": (
                "Runs locally through Ollama and can work "
                "without internet after the model has been "
                "downloaded."
            ),
        },
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "LawMate common LLM service ready."
    )

    print(
        "Supported modes:"
    )

    for mode_name, mode_info in (
        get_llm_mode_info().items()
    ):

        print(
            f"- {mode_name}: "
            f"{mode_info['label']}"
        )