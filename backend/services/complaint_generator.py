import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
# SUPPORTED COMPLAINT TYPES
# ============================================================

SUPPORTED_COMPLAINT_TYPES = {
    "consumer",
    "cybercrime",
    "police",
    "workplace",
    "general",
}


COMPLAINT_TYPE_LABELS = {
    "consumer": "Consumer Complaint",
    "cybercrime": "Cybercrime Complaint",
    "police": "Police Complaint",
    "workplace": "Workplace Complaint",
    "general": "General Legal Complaint",
}


def clean_value(value):
    if value is None:
        return ""
    return str(value).strip()


def validate_complaint_data(
    complaint_type,
    problem_description,
):
    complaint_type = clean_value(
        complaint_type
    ).lower()

    problem_description = clean_value(
        problem_description
    )

    if complaint_type not in SUPPORTED_COMPLAINT_TYPES:
        raise ValueError(
            "Unsupported complaint type. "
            "Supported types are consumer, cybercrime, "
            "police, workplace, and general."
        )

    if len(problem_description) < 20:
        raise ValueError(
            "Please provide a more detailed description "
            "of the problem."
        )

    return complaint_type, problem_description


def generate_complaint(
    complaint_type,
    problem_description,
    complainant_name="",
    complainant_address="",
    complainant_contact="",
    opposite_party="",
    incident_date="",
    incident_location="",
    amount_involved="",
    evidence="",
    desired_relief="",
    uploaded_evidence_text="",
    uploaded_evidence_files=None,
):
    """
    Generate a structured complaint draft.

    Pasted evidence descriptions and uploaded evidence files
    are treated only as user-supplied material.
    LawMate does not authenticate evidence.
    """

    complaint_type, problem_description = (
        validate_complaint_data(
            complaint_type,
            problem_description,
        )
    )

    complaint_label = (
        COMPLAINT_TYPE_LABELS[
            complaint_type
        ]
    )

    complainant_name = clean_value(complainant_name)
    complainant_address = clean_value(complainant_address)
    complainant_contact = clean_value(complainant_contact)
    opposite_party = clean_value(opposite_party)
    incident_date = clean_value(incident_date)
    incident_location = clean_value(incident_location)
    amount_involved = clean_value(amount_involved)
    evidence = clean_value(evidence)
    desired_relief = clean_value(desired_relief)
    uploaded_evidence_text = clean_value(
        uploaded_evidence_text
    )

    uploaded_evidence_files = (
        uploaded_evidence_files or []
    )

    evidence_filenames = (
        "\n".join(
            f"- {filename}"
            for filename in uploaded_evidence_files
        )
        if uploaded_evidence_files
        else "[No evidence files uploaded]"
    )

    user_information = f"""
Complaint Type:
{complaint_label}

Complainant Name:
{complainant_name or "[Not provided]"}

Complainant Address:
{complainant_address or "[Not provided]"}

Complainant Contact:
{complainant_contact or "[Not provided]"}

Opposite Party / Respondent:
{opposite_party or "[Not provided]"}

Incident Date:
{incident_date or "[Not provided]"}

Incident Location:
{incident_location or "[Not provided]"}

Amount Involved:
{amount_involved or "[Not provided]"}

Evidence Description Entered by User:
{evidence or "[Not provided]"}

Uploaded Evidence Files:
{evidence_filenames}

Desired Relief:
{desired_relief or "[Not provided]"}

Problem Description:
{problem_description}
"""

    uploaded_evidence_context = (
        uploaded_evidence_text
        if uploaded_evidence_text
        else "[No readable uploaded evidence text was provided]"
    )

    prompt = f"""
You are LawMate AI, an Indian legal complaint drafting assistant.

Prepare a formal complaint draft using ONLY the facts supplied
by the user and the user-supplied supporting material below.

IMPORTANT RULES:

1. Do not invent names, addresses, dates, amounts, witnesses,
   transactions, case numbers, events, legal sections, Acts,
   penalties, judgments, or constitutional provisions.

2. Text typed or pasted into Evidence Description is
   USER-PROVIDED and UNVERIFIED. It may have been edited.
   Never describe it as proven or authenticated evidence.

3. Uploaded files are also USER-SUPPLIED. LawMate may extract
   and summarize their contents, but MUST NOT claim that files,
   screenshots, chats, receipts, images, or documents are
   genuine, original, unaltered, legally admissible, or
   independently verified.

4. If supporting material conflicts with the problem
   description, do not guess. Tell the user to review the
   inconsistency.

5. Prefer careful wording such as:
   "The complainant states..."
   "The complainant has supplied..."
   "Supporting material supplied by the complainant indicates..."

   Never say:
   "This proves..."
   "The evidence establishes..."
   "The screenshot confirms..."

6. If an important fact is missing, use a clear placeholder
   or omit the unsupported detail.

7. Keep the complaint factual, respectful, professional,
   and suitable for review.

8. The output is a DRAFT and must be reviewed before submission.

USER INFORMATION:

{user_information}

EXTRACTED CONTENT FROM USER-UPLOADED EVIDENCE:

{uploaded_evidence_context}

OUTPUT FORMAT:

# {complaint_label}

## To

Use the likely recipient only when reasonably inferable.
Otherwise use [Insert Appropriate Authority].

## Subject

Write a short professional subject.

## Complainant Details

Name:
Address:
Contact:

## Opposite Party / Respondent

Use only supplied information or a placeholder.

## Facts of the Complaint

Write numbered chronological points using supplied facts only.

## Supporting Material Supplied by Complainant

### User-Provided Evidence Description

Summarize what the user typed or pasted and clearly label
it as unverified user-provided information.

### Uploaded Supporting Files

List uploaded filenames when available. Briefly describe
relevant extracted content using cautious wording. State
clearly that LawMate has not verified authenticity,
originality, or legal admissibility.

## Relief / Action Requested

Use the user's requested relief. If none was supplied,
suggest only neutral general action.

## Declaration

Include a short declaration that the supplied facts are true
to the complainant's knowledge.

## Place and Date

Place:
Date:

## Signature

Complainant Signature:

____________________________

Name:

## LawMate Drafting Note

State that the draft was generated from user-provided facts
and user-supplied supporting material and that LawMate does
not authenticate evidence.

## Disclaimer

State that LawMate provides drafting assistance and does not
replace professional legal advice.
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return {
        "complaint_type": complaint_type,
        "complaint_label": complaint_label,
        "draft": response.text,
    }


if __name__ == "__main__":
    print(
        "LawMate Complaint Generator service ready."
    )
    print(
        "Supported complaint types:"
    )

    for complaint_type in sorted(
        SUPPORTED_COMPLAINT_TYPES
    ):
        print(
            f"- {complaint_type}"
        )
