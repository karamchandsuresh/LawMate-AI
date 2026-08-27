from services.llm_service import (
    generate_ai_response,
    normalize_llm_mode,
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

def normalize_language(language):
    """
    Normalize a language code or label to the lowercase
    language names used by LawMate.
    """

    if not language:
        return "english"

    normalized = str(language).strip().lower()

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

    normalized = aliases.get(
        normalized,
        normalized,
    )

    return (
        normalized
        if normalized in SUPPORTED_LANGUAGES
        else "english"
    )


# ============================================================
# LOCAL SCRIPT DETECTION
# ============================================================

def _contains_range(text, start, end):
    return any(
        start <= ord(character) <= end
        for character in text
    )


def detect_script_language(text):
    """
    Detect common Indian-language scripts locally.

    This makes offline Local-Llama mode independent of Gemini
    for obvious script-based language detection.
    """

    if not text or not text.strip():
        return "english"

    # Malayalam
    if _contains_range(text, 0x0D00, 0x0D7F):
        return "malayalam"

    # Tamil
    if _contains_range(text, 0x0B80, 0x0BFF):
        return "tamil"

    # Telugu
    if _contains_range(text, 0x0C00, 0x0C7F):
        return "telugu"

    # Kannada
    if _contains_range(text, 0x0C80, 0x0CFF):
        return "kannada"

    # Bengali
    if _contains_range(text, 0x0980, 0x09FF):
        return "bengali"

    # Gujarati
    if _contains_range(text, 0x0A80, 0x0AFF):
        return "gujarati"

    # Gurmukhi / Punjabi
    if _contains_range(text, 0x0A00, 0x0A7F):
        return "punjabi"

    # Arabic-derived script. For LawMate's supported set,
    # treat it as Urdu.
    if (
        _contains_range(text, 0x0600, 0x06FF)
        or _contains_range(text, 0x0750, 0x077F)
    ):
        return "urdu"

    # Devanagari can represent Hindi or Marathi.
    # Use Hindi as the safe V1 default and allow the model
    # detector below to refine it when needed.
    if _contains_range(text, 0x0900, 0x097F):
        return "hindi"

    return None


# ============================================================
# DETECT LANGUAGE
# ============================================================

def detect_language(
    text,
    model_mode="auto",
):
    """
    Detect the main language of a user message.

    Script detection is attempted locally first. If the script
    is ambiguous or primarily Latin, the selected AI provider
    may refine the result.
    """

    if not text or not text.strip():
        return "english"

    script_language = detect_script_language(text)

    if script_language:
        return script_language

    model_mode = normalize_llm_mode(
        model_mode
    )

    prompt = f"""
You are a language detection system.

Detect the primary language of the text below.

Return ONLY one lowercase language name from this list:

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

If the message is mainly English, return english.
If uncertain, return english.

TEXT:

{text}
"""

    try:
        result = generate_ai_response(
            prompt=prompt,
            mode=model_mode,
        )

        detected = normalize_language(
            result["text"]
            .strip()
            .lower()
            .splitlines()[0]
        )

        return detected

    except Exception as error:
        print(
            "Language detection error:",
            error,
        )
        return "english"


# ============================================================
# TRANSLATE TO ENGLISH
# ============================================================

def translate_to_english(
    text,
    source_language,
    model_mode="auto",
):
    """
    Translate user text to English using the currently
    selected LawMate AI provider.
    """

    source_language = normalize_language(
        source_language
    )

    if (
        source_language == "english"
        or not text.strip()
    ):
        return text.strip()

    model_mode = normalize_llm_mode(
        model_mode
    )

    prompt = f"""
Translate the following text from {source_language}
to natural English.

IMPORTANT RULES:

1. Preserve the original meaning exactly.
2. Do not answer the question.
3. Do not add legal advice.
4. Do not summarize.
5. Preserve names, dates, monetary amounts, law names,
   case names, section numbers, and factual details.
6. Return ONLY the English translation.

TEXT:

{text}
"""

    result = generate_ai_response(
        prompt=prompt,
        mode=model_mode,
    )

    return result["text"].strip()




def _contains_target_script(text, language):
    """
    Check whether translated output visibly contains the target script.
    This is used only as a quality guard for local-model translation.
    """

    ranges = {
        "malayalam": (0x0D00, 0x0D7F),
        "tamil": (0x0B80, 0x0BFF),
        "telugu": (0x0C00, 0x0C7F),
        "kannada": (0x0C80, 0x0CFF),
        "bengali": (0x0980, 0x09FF),
        "gujarati": (0x0A80, 0x0AFF),
        "punjabi": (0x0A00, 0x0A7F),
        "hindi": (0x0900, 0x097F),
        "marathi": (0x0900, 0x097F),
        "urdu": (0x0600, 0x06FF),
    }

    script_range = ranges.get(language)

    if not script_range:
        return True

    start, end = script_range

    return any(
        start <= ord(character) <= end
        for character in text
    )


# ============================================================
# TRANSLATE FROM ENGLISH
# ============================================================

def translate_from_english(
    text,
    target_language,
    model_mode="auto",
):
    """
    Translate LawMate's final English response to the selected
    interface language using the selected AI provider.
    """

    target_language = normalize_language(
        target_language
    )

    if (
        target_language == "english"
        or not text.strip()
    ):
        return text.strip()

    model_mode = normalize_llm_mode(
        model_mode
    )

    prompt = f"""
Translate the following LawMate AI response from English
to {target_language}.

IMPORTANT RULES:

1. Translate the explanatory text into {target_language}.
2. Preserve the legal meaning exactly.
3. Preserve Markdown formatting, headings, and bullet points.
4. Preserve section numbers, dates, monetary amounts,
   source labels, and citations.
5. Keep official Indian Act and case names in English when
   translating the name would make identification unclear.
6. Do not remove disclaimers or grounding notices.
7. Do not add new legal information.
8. Return ONLY the translated response.
9. The final response must be primarily in {target_language},
   except for official names, citations, and unavoidable
   technical/legal terms.

TEXT:

{text}
"""

    result = generate_ai_response(
        prompt=prompt,
        mode=model_mode,
    )

    translated = result["text"].strip()

    # Small local models can occasionally answer the content instead
    # of translating it. For Local Llama, verify that the requested
    # Indian-language script is actually present and retry once with
    # an even stricter translation-only instruction.
    if (
        model_mode == "llama"
        and target_language != "english"
        and not _contains_target_script(
            translated,
            target_language,
        )
    ):
        retry_prompt = f"""
STRICT TRANSLATION TASK.

Translate ALL readable explanatory text below into {target_language}.

Do not answer, explain, summarize, or discuss the content.
Do not leave ordinary English sentences untranslated.
Keep only official Indian law names, source citations, section
numbers, dates, and unavoidable legal names in English.

Your output MUST visibly use the native script of
{target_language}.

Return ONLY the translated text.

TEXT:

{text}
"""

        retry_result = generate_ai_response(
            prompt=retry_prompt,
            mode="llama",
        )

        retry_text = retry_result["text"].strip()

        if _contains_target_script(
            retry_text,
            target_language,
        ):
            translated = retry_text

    return translated


# ============================================================
# PREPARE USER QUERY
# ============================================================

def prepare_multilingual_query(
    text,
    model_mode="auto",
):
    """
    Complete input-side multilingual pipeline:

    user message
        ↓
    local/model-assisted language detection
        ↓
    selected-provider translation to English if required
    """

    original_text = text.strip()

    language = detect_language(
        original_text,
        model_mode=model_mode,
    )

    english_text = translate_to_english(
        original_text,
        language,
        model_mode=model_mode,
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
    user_language,
    model_mode="auto",
):
    """
    Translate the final LawMate response into the requested
    response language when needed.
    """

    return translate_from_english(
        english_response,
        user_language,
        model_mode=model_mode,
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

    print("Detected:")
    print(
        detect_language(
            test_message,
            model_mode="llama",
        )
    )
