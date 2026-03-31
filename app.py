# app.py — AaykarAI Complete Version
from datetime import date
import streamlit as st
import json
import os
from groq import Groq
from tools import calculate_tax, find_exemptions, compare_regimes, get_itr_form, calculate_rental_income, whatif_analysis
from dotenv import load_dotenv
from pdf_extractor import process_form16
from pdf_generator import generate_tax_report

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="AaykarAI", page_icon="🇮🇳", layout="centered")

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Nuclear background fix — targets every possible selector ── */
html { background-color: #1a1a1a !important; }
body { background-color: #1a1a1a !important; }
#root { background-color: #1a1a1a !important; }
.stApp { background-color: #1a1a1a !important; }
.stApp > div { background-color: #1a1a1a !important; }
.stApp > div > div { background-color: #1a1a1a !important; }
.stApp > div > div > div { background-color: #1a1a1a !important; }
[data-testid="stAppViewContainer"] { background-color: #1a1a1a !important; }
[data-testid="stAppViewContainer"] { background-color: #1a1a1a !important; }
[data-testid="stMain"] { background-color: #1a1a1a !important; }
[data-testid="stMainBlockContainer"] { background-color: #1a1a1a !important; }
.main { background-color: #1a1a1a !important; }
section.main { background-color: #1a1a1a !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Content width ── */
.block-container {
    max-width: 760px !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* ── Sidebar — dark minimal ── */
[data-testid="stSidebar"] {
    background-color: #1a1a1a !important;
    border-right: 1px solid #2a2a2a !important;
}
[data-testid="stSidebar"] > div {
    background-color: #1a1a1a !important;
}
[data-testid="stSidebar"] > div > div {
    background-color: #1a1a1a !important;
}
[data-testid="stSidebar"] * {
    color: #888 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
}
[data-testid="stSidebar"] .stButton > button {
    background-color: #2a2a2a !important;
    color: #aaa !important;
    border: 1px solid #333 !important;
    border-radius: 6px !important;
    width: 100% !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #333 !important;
    color: #fff !important;
    border-color: #444 !important;
}

/* ── Main header ── */
.main-header {
    text-align: center;
    padding: 1.5rem 0 1rem;
    margin-bottom: 0.5rem;
}
.main-header h1 {
    font-size: 1.6rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
    letter-spacing: -0.02em;
}
.main-header p {
    font-size: 0.82rem;
    color: #999;
    margin: 0.25rem 0 0;
    font-weight: 400;
}

/* ── Tool indicator ── */
.tool-indicator {
    background: #2a2a2a;
    border-left: 2px solid #bbb;
    padding: 0.3rem 0.75rem;
    border-radius: 0 4px 4px 0;
    font-size: 0.76rem;
    color: #999;
    margin: 0.2rem 0;
    font-family: 'DM Mono', monospace;
}

/* ── Chat messages ── */
[data-testid="stChatInputTextArea"] {
    color: #ffffff !important;
    caret-color: #ffffff !important;
}
.st-emotion-cache-1ab1jlb textarea {
    color: #ffffff !important;
}
textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── Chat input — every possible selector ── */
[data-testid="stChatInput"] {
    background-color: #2a2a2a !important;
}
[data-testid="stChatInputContainer"] {
    background-color: #1a1a1a !important;
}
[data-testid="stBottomBlockContainer"] {
    background-color: #1a1a1a !important;
}
.st-emotion-cache-hzygls {
    background-color: #1a1a1a !important;
}
[data-testid="stChatInput"] textarea {
    background-color: #2a2a2a !important;
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] > div {
    background-color: #2a2a2a !important;
}
.stChatInput {
    background-color: #2a2a2a !important;
}
.stChatInput > div {
    background-color: #2a2a2a !important;
    border-radius: 12px !important;
}



/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background-color: #2a2a2a !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background-color: #2a2a2a !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    border: 1px solid #333333  !important;
}
[data-testid="stMetricLabel"] p {
    color: #999 !important;
    font-size: 0.74rem !important;
}
[data-testid="stMetricValue"] {
    color: #1a1a1a !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1.05rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background-color: #2a2a2a !important;
    border: 1px solid #333333  !important;
    border-radius: 8px !important;
}
[data-testid="stExpanderDetails"] {
    background-color: #2a2a2a !important;
}

/* ── Divider ── */
hr {
    border-color: #333333  !important;
    margin: 0.75rem 0 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.84rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #888 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🇮🇳 AaykarAI</h1>
    <p>Indian Tax Assistant • FY 2024-25</p>
</div>
""", unsafe_allow_html=True)

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are AaykarAI — an expert Indian tax assistant for FY 2024-25 (AY 2025-26).

QUERY CLASSIFICATION — classify every user message into one of these types:

TYPE 1 — GENERAL TAX QUESTION (answer directly, no data collection)
Examples: "What is 80C?", "What is LTCG?", "When is ITR deadline?", "What are tax slabs?"
→ Answer directly from your knowledge. Be concise and clear.

TYPE 2 — OUT OF SCOPE (politely decline)
Examples: "What stocks should I buy?", "How do I start a business?", "Cricket score?"
→ Say: "I'm a tax assistant and can only help with Indian income tax queries."

TYPE 3 — WHAT-IF QUESTION (needs income data first)
Examples: "If I invest 50k in PPF how much tax do I save?", "What if I buy a house?", "Max deduction if I buy property?"
→ If income data already collected, output what-if JSON
→ If not, collect income first then answer

TYPE 4 — FULL TAX CALCULATION (collect data then calculate)
Examples: "Calculate my tax", "How much tax do I pay?", "What is my tax liability?"
→ Collect all data conversationally then output calculation JSON

COLLECTION CHECKLIST:
- annual_income (normal income from salary or business only, NOT capital gains or rental)
    COLLECTION CHECKLIST:
    - annual_income: ONLY salary or business income. If user says "my income is 80L including 20L stock profits", then annual_income = 60L and stcg = 20L. ALWAYS subtract capital gains and rental from the total before setting annual_income.
    - income_sources: list from [salary, business, capital_gains, house_property, interest, rental]
    - stcg: ONLY short term capital gains (stocks held LESS than 1 year). Never include this in annual_income.
    - ltcg: ONLY long term capital gains (stocks held MORE than 1 year). Never include this in annual_income.
    - annual_rent_received + municipal_tax_paid (if rental income. Never include rent in annual_income)
    - investments_80c (PPF, ELSS, LIC, NSC combined)
    - health_insurance_premium
    - nps_contribution
    - hra_received, basic_salary, rent_paid (annual), city_type (metro/non-metro)
    - home_loan_interest, education_loan_interest
    - age

    CRITICAL SEPARATION RULE:
    annual_income = total income MINUS capital gains MINUS rental income
    Example: "I earn 80L, 20L is stock profit held 6 months"
    → annual_income = 6000000 (60L business)
    → stcg = 2000000 (20L)
    → ltcg = 0
    NEVER put capital gains inside annual_income.
- income_sources: list from [salary, business, capital_gains, house_property, interest, rental]
- stcg (short term capital gains — stocks/assets held LESS than 1 year) — taxed at 20% flat
- ltcg (long term capital gains — stocks/assets held MORE than 1 year) — taxed at 12.5% above 1.25L
- annual_rent_received + municipal_tax_paid (if rental income)
- investments_80c (PPF, ELSS, LIC, NSC combined)
- health_insurance_premium
- nps_contribution
- hra_received, basic_salary, rent_paid (annual), city_type (metro/non-metro)
- home_loan_interest, education_loan_interest
- age

IMPORTANT RULES:
- Ask 2-3 questions at a time, never dump everything at once
- Convert Indian formats: 1 LPA=100000, 10 LPA=1000000, 1 crore=10000000
- For capital gains ALWAYS ask: held more or less than 1 year?
- If user says "stock profits" or "share market" ask about holding period
- Capital gains and rental income are SEPARATE from annual_income
- Missing optional fields default to 0

WHEN READY FOR FULL CALCULATION output EXACTLY this JSON block and nothing else:
```json
{
  "ready": true,
  "query_type": "calculation",
  "annual_income": 1200000,
  "income_sources": ["salary"],
  "stcg": 0,
  "ltcg": 0,
  "annual_rent_received": 0,
  "municipal_tax_paid": 0,
  "investments_80c": 150000,
  "health_insurance_premium": 15000,
  "hra_received": 0,
  "basic_salary": 0,
  "rent_paid": 0,
  "city_type": "non-metro",
  "home_loan_interest": 0,
  "education_loan_interest": 0,
  "nps_contribution": 0,
  "age": 30
}
```

WHEN READY FOR WHAT-IF output EXACTLY this JSON block and nothing else:
```json
{
  "ready": true,
  "query_type": "whatif",
  "annual_income": 1200000,
  "income_sources": ["salary"],
  "stcg": 0,
  "ltcg": 0,
  "annual_rent_received": 0,
  "municipal_tax_paid": 0,
  "current_profile": {
    "investments_80c": 100000,
    "health_insurance_premium": 15000,
    "age": 30
  },
  "proposed_changes": {
    "home_loan_interest": 200000
  }
}
```

Never output JSON unless you have all required fields. Never add text before or after the JSON."""

# ── JSON extractor ────────────────────────────────────────────────────────────

def extract_json(text: str):
    try:
        start = text.find("```json")
        end = text.find("```", start + 6)
        if start != -1 and end != -1:
            return json.loads(text[start + 7:end].strip())
    except:
        pass
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    return None

# ── Run all tax calculations ──────────────────────────────────────────────────

def run_tax_calculations(data: dict) -> dict:
    annual_income = data.get("annual_income", 0)
    stcg = data.get("stcg", 0)
    ltcg = data.get("ltcg", 0)

    # Rental income
    rental_net = 0
    rental_result = None
    if data.get("annual_rent_received", 0) > 0:
        rental_result = calculate_rental_income(
            data["annual_rent_received"],
            data.get("municipal_tax_paid", 0)
        )
    rental_net = rental_result["net_rental_income"] if rental_result else 0

    user_profile = {
        "investments_80c": data.get("investments_80c", 0),
        "health_insurance_premium": data.get("health_insurance_premium", 0),
        "hra_received": data.get("hra_received", 0),
        "basic_salary": data.get("basic_salary", 0),
        "rent_paid": data.get("rent_paid", 0),
        "city_type": data.get("city_type", "non-metro"),
        "home_loan_interest": data.get("home_loan_interest", 0),
        "education_loan_interest": data.get("education_loan_interest", 0),
        "nps_contribution": data.get("nps_contribution", 0),
        "age": data.get("age", 30)
    }

    query_type = data.get("query_type", "calculation")

    if query_type == "whatif":
        result = whatif_analysis(
            normal_income=annual_income,
            current_deductions=data.get("current_profile", {}),
            proposed_changes=data.get("proposed_changes", {}),
            stcg=stcg,
            ltcg=ltcg,
            rental_income_net=rental_net
        )
        return {"type": "whatif", "result": result}
    else:
        exemptions = find_exemptions(user_profile)
        total_deductions = exemptions["total_deductions"]
        comparison = compare_regimes(annual_income, total_deductions, stcg, ltcg, rental_net)
        itr_form = get_itr_form({
            "income_sources": data.get("income_sources", ["salary"]),
            "annual_income": annual_income + stcg + ltcg + rental_net
        })

        return {
            "type": "calculation",
            "exemptions": exemptions,
            "comparison": comparison,
            "itr_form": itr_form,
            "annual_income": annual_income,
            "stcg": stcg,
            "ltcg": ltcg,
            "rental_net": rental_net,
            "rental_detail": rental_result,
            "total_deductions": total_deductions
        }

# ── Format results ────────────────────────────────────────────────────────────
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = {}

def format_results(results: dict) -> str:
    if results["type"] == "whatif":
        r = results["result"]
        lines = [
            "✅ **What-If Analysis Complete!**\n",
            f"**💰 Current Tax:** ₹{r['current_tax']:,.0f}",
            f"**💰 Tax After Change:** ₹{r['proposed_tax']:,.0f}",
            f"**📉 Additional Deductions Unlocked:** ₹{r['additional_deductions']:,.0f}",
            f"\n🎯 **{r['verdict']}**",
            f"\n📝 Recommended regime after change: **{r['recommended_regime_after_change'].upper()}**",
            f"\n*⚠️ These are estimates. Consult a CA for final filing.*"
        ]
        return "\n".join(lines)

    comp = results["comparison"]
    itr = results["itr_form"]
    exemptions = results["exemptions"]
    rec = comp["recommended_regime"]
    tax = comp["new_regime_tax"] if rec == "new" else comp["old_regime_tax"]
    det = comp[f"{rec}_regime_details"]

    lines = [
        "✅ **Tax Calculation Complete!**\n",
        "**📊 Income Breakdown:**",
        f"- Normal Income (salary/business): ₹{results['annual_income']:,.0f}",
    ]

    if results["rental_net"] > 0:
        rd = results["rental_detail"]
        lines.append(f"- Rental Income (net after 30% deduction): ₹{results['rental_net']:,.0f}")
        lines.append(f"  *(Gross ₹{rd['annual_rent']:,.0f} → std deduction ₹{rd['standard_deduction_30_percent']:,.0f})*")

    if results["stcg"] > 0:
        cg = det["capital_gains_detail"]
        lines.append(f"- STCG (< 1 yr): ₹{results['stcg']:,.0f} → Tax @ 20% = **₹{cg['stcg_tax']:,.0f}**")

    if results["ltcg"] > 0:
        cg = det["capital_gains_detail"]
        lines.append(f"- LTCG (> 1 yr): ₹{results['ltcg']:,.0f} → Tax @ 12.5% (₹1.25L exempt) = **₹{cg['ltcg_tax']:,.0f}**")

    lines += [
        f"\n**🔢 Tax Computation ({rec.upper()} REGIME):**",
        f"- Taxable Slab Income: ₹{det['taxable_slab_income']:,.0f}",
        f"- Slab Tax: ₹{det['slab_tax']:,.0f}",
        f"- 87A Rebate: -₹{det['rebate_87a']:,.0f}",
        f"- Capital Gains Tax: ₹{det['capital_gains_tax']:,.0f}",
        f"- Surcharge: ₹{det['surcharge']:,.0f}",
        f"- Health & Education Cess (4%): ₹{det['cess']:,.0f}",
        f"- **Total Tax Payable: ₹{tax:,.0f}**",
        f"- Effective Tax Rate: {det['effective_rate']}%\n",
        f"**💰 Regime Comparison:**",
        f"- New Regime Tax: ₹{comp['new_regime_tax']:,.0f}",
        f"- Old Regime Tax: ₹{comp['old_regime_tax']:,.0f}",
        f"- {comp['reason']}\n",
    ]

    if exemptions["exemptions"]:
        lines.append("**🔖 Deductions Applied:**")
        for ex in exemptions["exemptions"]:
            lines.append(f"- Section {ex['section']}: ₹{ex['claimed']:,.0f} — {ex['description']}")
        lines.append(f"- **Total Deductions: ₹{results['total_deductions']:,.0f}**\n")

    lines += [
        f"**📝 ITR Form to File: {itr['recommended_form']}**",
        f"- {itr['reason']}",
        f"- Deadline: {itr['filing_deadline']}",
        f"- Late Fee: {itr['late_fee']}\n",
        "*⚠️ These are estimates. Please consult a CA for final filing.*"
    ]

    return "\n".join(lines)



# ── Session state ─────────────────────────────────────────────────────────────

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "display_messages" not in st.session_state:
    st.session_state.display_messages = [{
        "role": "assistant",
        "content": "Namaste! 🙏 I'm **AaykarAI**, your personal tax assistant for FY 2024-25.\n\nI can help you with:\n- 📊 Full tax calculation (salary, business, capital gains, rental)\n- 🔖 Finding all exemptions you qualify for\n- 💰 Old vs new regime comparison\n- 🤔 What-if analysis (e.g. 'if I invest X more, how much do I save?')\n- ❓ General tax questions\n\nWhat would you like help with today?"
    }]

if "calculated" not in st.session_state:
    st.session_state.calculated = False

if "form16_processed" not in st.session_state:
    st.session_state.form16_processed = False

if "last_results" not in st.session_state:
    st.session_state.last_results = None

if "last_user_info" not in st.session_state:
    st.session_state.last_user_info = {}

# ── PDF Download button ───────────────────────────────────────────────────────

if st.session_state.get("last_results"):
    from pdf_generator import generate_tax_report
    pdf_bytes = generate_tax_report(
        st.session_state.last_results,
        st.session_state.get("last_user_info", {})
    )
    st.download_button(
        label="📥 Download Tax Report PDF",
        data=pdf_bytes,
        file_name=f"AaykarAI_Tax_Report_{date.today()}.pdf",
        mime="application/pdf"
    )

# ── Display chat ──────────────────────────────────────────────────────────────

for msg in st.session_state.display_messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])
    elif msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    elif msg["role"] == "tool_indicator":
        st.markdown(
            f'<div class="tool-indicator">⚙️ {msg["content"]}</div>',
            unsafe_allow_html=True
        )

# ── Chat input ────────────────────────────────────────────────────────────────

if user_input := st.chat_input("Ask me anything about your taxes..."):

    st.session_state.display_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        tool_container = st.container()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2048,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.conversation_history
        )

        reply = response.choices[0].message.content
        parsed = extract_json(reply)

        if parsed and parsed.get("ready"):

            # Show indicators FIRST before calculating
            indicator_placeholder = st.empty()
            with indicator_placeholder.container():
                for label in [
                    "Calculating tax liability...",
                    "Finding exemptions...",
                    "Comparing regimes...",
                    "Determining ITR form..."
                ]:
                    st.markdown(
                        f'<div class="tool-indicator">⚙️ {label}</div>',
                        unsafe_allow_html=True
                    )
                    st.session_state.display_messages.append({
                        "role": "tool_indicator",
                        "content": label
                    })

            # Run calculations
            results = run_tax_calculations(parsed)
            final_answer = format_results(results)

            # Clear indicators, show result
            indicator_placeholder.empty()
            placeholder.markdown(final_answer)

            # Store results for PDF
            st.session_state.last_results = results
            st.session_state.last_user_info = {}

            st.session_state.display_messages.append({"role": "assistant", "content": final_answer})
            st.session_state.conversation_history.append({"role": "assistant", "content": final_answer})
            st.session_state.calculated = True

            # PDF download button RIGHT HERE inline
            pdf_bytes = generate_tax_report(results, {})
            st.download_button(
                label="📥 Download Tax Report PDF",
                data=pdf_bytes,
                file_name=f"AaykarAI_Tax_Report_{date.today()}.pdf",
                mime="application/pdf",
                key="pdf_download_chat"
            )
        else:
            placeholder.markdown(reply)
            st.session_state.display_messages.append({"role": "assistant", "content": reply})
            st.session_state.conversation_history.append({"role": "assistant", "content": reply})
            st.session_state.calculated = False

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### AaykarAI 🇮🇳")
    st.divider()
    if st.button("↺ New Calculation"):
        st.session_state.conversation_history = []
        st.session_state.display_messages = []
        st.session_state.calculated = False
        st.session_state.form16_processed = False
        st.session_state.last_results = None
        st.rerun()