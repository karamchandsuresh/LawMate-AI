import os

from dotenv import load_dotenv
from google import genai


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
# SUPPORTED CASE TYPES
# ============================================================

SUPPORTED_CASE_TYPES = {
    "consumer",
    "employment",
    "property",
    "family",
    "cybercrime",
    "criminal",
    "civil",
    "general",
}


# ============================================================
# CLEAN VALUE
# ============================================================

def clean_value(value):

    if value is None:
        return ""

    return str(
        value
    ).strip()


# ============================================================
# VALIDATION
# ============================================================

def validate_case_input(
    case_type,
    case_facts
):

    case_type = clean_value(
        case_type
    ).lower()

    case_facts = clean_value(
        case_facts
    )

    if (
        case_type
        not in SUPPORTED_CASE_TYPES
    ):

        raise ValueError(
            "Unsupported case type. "
            "Supported types are consumer, "
            "employment, property, family, "
            "cybercrime, criminal, civil, "
            "and general."
        )

    if len(case_facts) < 30:

        raise ValueError(
            "Please provide more detailed "
            "facts about the case."
        )

    return (
        case_type,
        case_facts
    )


# ============================================================
# CASE OUTCOME ASSESSMENT
# ============================================================

def assess_case(
    case_type,
    case_facts,
    user_role="",
    opposite_party="",
    evidence_summary="",
    desired_outcome="",
):

    """
    Provide cautious case guidance.

    This function does NOT predict a guaranteed
    court result.
    """

    (
        case_type,
        case_facts
    ) = validate_case_input(
        case_type,
        case_facts
    )

    user_role = clean_value(
        user_role
    )

    opposite_party = clean_value(
        opposite_party
    )

    evidence_summary = clean_value(
        evidence_summary
    )

    desired_outcome = clean_value(
        desired_outcome
    )


    prompt = f"""
You are LawMate AI, an Indian legal case-assessment assistant.

Analyze the user's case using ONLY the facts provided.

You are NOT a judge and you cannot predict a guaranteed
court result.

Do not claim that the user will win or lose.

Do not invent:

- legal sections
- judgments
- evidence
- dates
- witnesses
- facts
- penalties
- court findings

If important information is missing, clearly identify it.

============================================================
CASE INFORMATION
============================================================

Case Type:
{case_type}

User Role:
{user_role or "[Not provided]"}

Opposite Party:
{opposite_party or "[Not provided]"}

Case Facts:
{case_facts}

Evidence Summary:
{evidence_summary or "[Not provided]"}

Desired Outcome:
{desired_outcome or "[Not provided]"}

============================================================
ASSESSMENT RULES
============================================================

Use a qualitative assessment only.

Allowed outlook labels:

Favorable
Mixed / Uncertain
Weak
Insufficient Information

The outlook means only how the supplied facts appear,
not the actual result of any court or authority.

Consider:

1. clarity of facts
2. available supporting material
3. apparent consistency
4. missing information
5. possible legal issues
6. practical difficulties
7. whether professional legal advice may be needed

============================================================
OUTPUT FORMAT
============================================================

# ⚖️ Case Assessment

## Case Overview

Briefly summarize the dispute.

## User's Position

Explain the user's apparent position based only on
the supplied facts.

## Factors That May Support the Case

List relevant supporting factors.

## Factors That May Weaken or Complicate the Case

List weaknesses, uncertainties, missing details,
or practical difficulties.

## Evidence Considerations

Explain what supplied evidence may be useful and
what additional evidence may be important.

Do not claim that any evidence is authenticated.

## Qualitative Outlook

Choose exactly one:

Favorable
Mixed / Uncertain
Weak
Insufficient Information

Then briefly explain why.

## Possible Next Steps

Give practical general steps the user may consider.

## Important Limitations

Explain that actual outcomes depend on evidence,
applicable law, procedure, arguments, authorities,
and judicial interpretation.

## Disclaimer

State that LawMate AI provides general legal
information and case-assessment assistance only
and does not predict court outcomes or replace
professional legal advice.
"""


    response = (
        gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
    )


    return {
        "case_type": case_type,
        "assessment": response.text,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "LawMate Case Predictor service ready."
    )

    print(
        "Supported case types:"
    )

    for case_type in sorted(
        SUPPORTED_CASE_TYPES
    ):

        print(
            f"- {case_type}"
        )