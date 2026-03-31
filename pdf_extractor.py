# pdf_extractor.py — Extract tax data from Form 16 PDF

import os
import json
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Step 1: Extract raw text from PDF ────────────────────────────────────────

def extract_text_from_pdf(pdf_file) -> str:
    """
    Takes a file object (from Streamlit uploader)
    Returns all text extracted from every page
    """
    reader = PdfReader(pdf_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

# ── Step 2: Use Groq to parse the extracted text ──────────────────────────────

def extract_tax_data_from_text(raw_text: str) -> dict:
    """
    Sends raw PDF text to Groq
    Groq extracts structured tax data and returns JSON
    """

    prompt = f"""You are a tax document parser. Extract tax information from this Form 16 or salary document text.

Return ONLY a JSON object with these exact fields. Use 0 for missing fields. No extra text.

{{
  "name": "employee name or empty string",
  "pan": "PAN number or empty string",
  "employer": "employer name or empty string",
  "annual_income": "total gross salary in rupees as number",
  "basic_salary": "basic salary component as number",
  "hra_received": "HRA received as number",
  "investments_80c": "total 80C deductions (PF + LIC + others) as number",
  "health_insurance_premium": "80D health insurance as number",
  "home_loan_interest": "section 24 home loan interest as number",
  "nps_contribution": "80CCD NPS contribution as number",
  "tds_deducted": "total TDS already deducted as number",
  "standard_deduction": "standard deduction as number",
  "income_sources": ["salary"]
}}

DOCUMENT TEXT:
{raw_text[:4000]}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": "You are a tax document parser. Always return valid JSON only. No explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    reply = response.choices[0].message.content

    # Parse JSON from response
    try:
        # Try with backticks first
        start = reply.find("```json")
        end = reply.find("```", start + 6)
        if start != -1 and end != -1:
            return json.loads(reply[start + 7:end].strip())
    except:
        pass

    try:
        # Try raw JSON
        start = reply.find("{")
        end = reply.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(reply[start:end])
    except:
        pass

    # Return empty profile if parsing fails
    return {}

# ── Step 3: Main function — combines both steps ───────────────────────────────

def process_form16(pdf_file) -> dict:
    """
    Main function called from app.py
    Takes uploaded PDF file
    Returns structured tax data dict
    """
    print("Extracting text from PDF...")
    raw_text = extract_text_from_pdf(pdf_file)

    if not raw_text.strip():
        raise ValueError("Could not extract text from this PDF. It may be scanned/image-based.")

    print("Parsing tax data from extracted text...")
    tax_data = extract_tax_data_from_text(raw_text)

    # Add ready flag so app.py knows it can calculate
    tax_data["ready"] = True
    tax_data["query_type"] = "calculation"

    # Set defaults for fields not in Form 16
    defaults = {
        "stcg": 0,
        "ltcg": 0,
        "annual_rent_received": 0,
        "municipal_tax_paid": 0,
        "rent_paid": 0,
        "city_type": "non-metro",
        "education_loan_interest": 0,
        "age": 30
    }

    for key, value in defaults.items():
        if key not in tax_data:
            tax_data[key] = value

    return tax_data