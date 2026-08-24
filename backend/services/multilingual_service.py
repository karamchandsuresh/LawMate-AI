from dotenv import load_dotenv
from google import genai
import os


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

GEMINI_MODEL = "gemini-3.1-flash-lite"

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# SUPPORTED LANGUAGE LABELS
# ============================================================

SUPPORTED_LANGUAGES = {
    "english",
    "hindi",
    "malayalam",
    "tamil",
    "telugu",
    "kannada",
    "bengali",
    "marathi",
    "gujarati",
    "punjabi",
    "urdu",
}


# ============================================================
# NORMALIZE LANGUAGE
# ============================================================

def normalize_language(
    language
):
    """
    Normalize the detected language label.
    """

    if not language:
        return "english"

    normalized = (
        language
        .strip()
        .lower()
    )

    aliases = {
        "en": "english",
        "eng": "english",
        "hi": "hindi",
        "ml": "malayalam",
        "ta": "tamil",
        "te": "telugu",
        "kn": "kannada",
        "bn": "bengali",
        "mr": "marathi",
        "gu": "gujarati",
        "pa": "punjabi",
        "ur": "urdu",
    }

    return aliases.get(
        normalized,
        normalized
    )


# ============================================================
# DETECT LANGUAGE
# ============================================================

def detect_language(
    text
):
    """
    Detect the main language used in the user's message.

    Returns a simple lowercase language name.
    """

    if not text or not text.strip():
        return "english"

    prompt = f"""
You are a language detection system.

Detect the primary language of the text below.

Return ONLY one lowercase language name.

Preferred labels:

english
hindi
malayalam
tamil
telugu
kannada
bengali
marathi
gujarati
punjabi
urdu

If the message contains a mixture of English and another
language, return the main language used by the user.

If you are uncertain, return:

english

TEXT:

{text}
"""

    try:

        response = (
            gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
        )

        detected_language = (
            response.text
            .strip()
            .lower()
        )

        detected_language = (
            normalize_language(
                detected_language
            )
        )

        if (
            detected_language
            not in SUPPORTED_LANGUAGES
        ):
            return "english"

        return detected_language

    except Exception as error:

        print(
            "Language detection error:",
            error
        )

        return "english"


# ============================================================
# TRANSLATE TO ENGLISH
# ============================================================

def translate_to_english(
    text,
    source_language
):
    """
    Translate a user message to English.

    English input is returned unchanged.
    """

    source_language = (
        normalize_language(
            source_language
        )
    )

    if (
        source_language == "english"
        or not text.strip()
    ):
        return text.strip()

    prompt = f"""
Translate the following text from {source_language}
to natural English.

IMPORTANT RULES:

1. Preserve the original meaning exactly.

2. Do not add legal advice.

3. Do not answer the question.

4. Do not summarize.

5. Preserve names, dates, amounts, law names,
   case names, section numbers, and other factual details.

6. Return ONLY the English translation.

TEXT:

{text}
"""

    response = (
        gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    )

    return (
        response.text
        .strip()
    )


# ============================================================
# TRANSLATE FROM ENGLISH
# ============================================================

def translate_from_english(
    text,
    target_language
):
    """
    Translate an English LawMate response back
    to the user's original language.

    English output is returned unchanged.
    """

    target_language = (
        normalize_language(
            target_language
        )
    )

    if (
        target_language == "english"
        or not text.strip()
    ):
        return text.strip()

    prompt = f"""
Translate the following LawMate AI response from English
to {target_language}.

IMPORTANT RULES:

1. Preserve the legal meaning.

2. Preserve Markdown formatting.

3. Preserve headings and bullet points.

4. Preserve section numbers, Act names, case names,
   dates, monetary amounts, source labels, and citations.

5. Do not remove disclaimers or verification notices.

6. Do not add new legal information.

7. Keep official Indian law names in English where
   translating them would make identification unclear.

8. Return ONLY the translated response.

TEXT:

{text}
"""

    response = (
        gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    )

    return (
        response.text
        .strip()
    )


# ============================================================
# PREPARE USER QUERY
# ============================================================

def prepare_multilingual_query(
    text
):
    """
    Complete input-side multilingual pipeline:

    user message
        ↓
    detect language
        ↓
    translate to English if required
    """

    original_text = text.strip()

    language = detect_language(
        original_text
    )

    english_text = (
        translate_to_english(
            original_text,
            language
        )
    )

    return {
        "original_text": original_text,
        "language": language,
        "english_text": english_text,
    }


# ============================================================
# PREPARE RESPONSE
# ============================================================

def prepare_multilingual_response(
    english_response,
    user_language
):
    """
    Translate the final English LawMate response
    back to the user's language when needed.
    """

    return translate_from_english(
        english_response,
        user_language
    )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "LawMate Multilingual Service ready."
    )

    test_message = (
        "എനിക്ക് എന്റെ തൊഴിലുടമ ശമ്പളം നൽകിയിട്ടില്ല. "
        "ഞാൻ എന്ത് ചെയ്യണം?"
    )

    print()
    print(
        "Original:"
    )
    print(
        test_message
    )

    result = (
        prepare_multilingual_query(
            test_message
        )
    )

    print()
    print(
        "Detected Language:"
    )
    print(
        result["language"]
    )

    print()
    print(
        "English Translation:"
    )
    print(
        result["english_text"]
    )

    sample_answer = (
        "You may consider asking your employer "
        "for the unpaid salary in writing."
    )

    translated_answer = (
        prepare_multilingual_response(
            sample_answer,
            result["language"]
        )
    )

    print()
    print(
        "Translated Response:"
    )
    print(
        translated_answer
    )