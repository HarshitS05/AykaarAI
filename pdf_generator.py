# pdf_generator.py — Generate ITR summary PDF using ReportLab

import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Colors ────────────────────────────────────────────────────────────────────

SAFFRON = colors.HexColor("#FF9933")
DARK_BLUE = colors.HexColor("#1a1a2e")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
GREEN = colors.HexColor("#00A550")
WHITE = colors.white
BLACK = colors.black

# ── Main generator ────────────────────────────────────────────────────────────

def generate_tax_report(results: dict, user_info: dict = {}) -> bytes:
    """
    Takes results dict from run_tax_calculations()
    Returns PDF as bytes (for Streamlit download button)
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Custom styles ─────────────────────────────────────────────────────────

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=22,
        textColor=WHITE,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=WHITE,
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=4
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=13,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        spaceBefore=6,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "Normal2",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BLACK,
        fontName="Helvetica",
        spaceAfter=4
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique"
    )

    # ── Header block ──────────────────────────────────────────────────────────

    header_data = [
        [Paragraph("🇮🇳 AaykarAI", title_style)],
        [Paragraph("Indian Tax Summary Report • FY 2024-25 (AY 2025-26)", subtitle_style)],
        [Paragraph(f"Generated on {date.today().strftime('%d %B %Y')}", subtitle_style)]
    ]

    header_table = Table(header_data, colWidths=[6.5 * inch])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1a1a1a")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    # ── Taxpayer info (if from Form 16) ───────────────────────────────────────

    if user_info.get("name") or user_info.get("pan"):
        info_data = [
            ["Taxpayer Name", user_info.get("name", "—")],
            ["PAN", user_info.get("pan", "—")],
            ["Employer", user_info.get("employer", "—")],
        ]

        info_table = Table(info_data, colWidths=[2.5 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUND", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 0.15 * inch))

    # ── Pull data from results ────────────────────────────────────────────────

    comp = results["comparison"]
    rec = comp["recommended_regime"]
    tax = comp["new_regime_tax"] if rec == "new" else comp["old_regime_tax"]
    det = comp[f"{rec}_regime_details"]
    exemptions = results["exemptions"]

    # ── Income breakdown section ──────────────────────────────────────────────

    section_header = Table(
        [[Paragraph("📊  Income Breakdown", section_style)]],
        colWidths=[6.5 * inch]
    )
    section_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(section_header)
    elements.append(Spacer(1, 0.05 * inch))

    income_data = [
        ["Income Source", "Amount (₹)"],
        ["Normal Income (Salary/Business)", f"₹{results['annual_income']:,.0f}"],
    ]

    if results.get("rental_net", 0) > 0:
        income_data.append(["Rental Income (Net after 30% deduction)", f"₹{results['rental_net']:,.0f}"])

    if results.get("stcg", 0) > 0:
        income_data.append([f"Short Term Capital Gains (STCG @ 20%)", f"₹{results['stcg']:,.0f}"])

    if results.get("ltcg", 0) > 0:
        income_data.append([f"Long Term Capital Gains (LTCG @ 12.5%)", f"₹{results['ltcg']:,.0f}"])

    income_data.append(["Standard Deduction", f"-₹{det['standard_deduction']:,.0f}"])
    income_data.append(["Total Taxable Slab Income", f"₹{det['taxable_slab_income']:,.0f}"])

    income_table = Table(income_data, colWidths=[4.5 * inch, 2 * inch])
    income_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUND", (0, 1), (-1, -2), [WHITE, LIGHT_GRAY]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f5e9")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(income_table)
    elements.append(Spacer(1, 0.15 * inch))

    # ── Tax computation section ───────────────────────────────────────────────

    section_header2 = Table(
        [[Paragraph(f"🔢  Tax Computation ({rec.upper()} REGIME — RECOMMENDED)", section_style)]],
        colWidths=[6.5 * inch]
    )
    section_header2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(section_header2)
    elements.append(Spacer(1, 0.05 * inch))

    tax_data = [
        ["Component", "Amount (₹)"],
        ["Slab Tax", f"₹{det['slab_tax']:,.0f}"],
        ["87A Rebate", f"-₹{det['rebate_87a']:,.0f}"],
        ["Capital Gains Tax", f"₹{det['capital_gains_tax']:,.0f}"],
        ["Surcharge", f"₹{det['surcharge']:,.0f}"],
        ["Health & Education Cess (4%)", f"₹{det['cess']:,.0f}"],
        ["TOTAL TAX PAYABLE", f"₹{tax:,.0f}"],
        ["Effective Tax Rate", f"{det['effective_rate']}%"],
    ]

    tax_table = Table(tax_data, colWidths=[4.5 * inch, 2 * inch])
    tax_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -2), (-1, -2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUND", (0, 1), (-1, -3), [WHITE, LIGHT_GRAY]),
        ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#fff3e0")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f5e9")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(tax_table)
    elements.append(Spacer(1, 0.15 * inch))

    # ── Regime comparison section ─────────────────────────────────────────────

    section_header3 = Table(
        [[Paragraph("💰  Regime Comparison", section_style)]],
        colWidths=[6.5 * inch]
    )
    section_header3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(section_header3)
    elements.append(Spacer(1, 0.05 * inch))

    regime_data = [
        ["Regime", "Tax Amount", "Recommended"],
        ["New Regime", f"₹{comp['new_regime_tax']:,.0f}", "✓" if rec == "new" else ""],
        ["Old Regime", f"₹{comp['old_regime_tax']:,.0f}", "✓" if rec == "old" else ""],
        ["Savings with recommended", f"₹{comp['savings_with_recommended']:,.0f}", ""],
    ]

    regime_table = Table(regime_data, colWidths=[3 * inch, 2 * inch, 1.5 * inch])
    regime_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUND", (0, 1), (-1, -2), [WHITE, LIGHT_GRAY]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f5e9")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(regime_table)
    elements.append(Spacer(1, 0.15 * inch))

    # ── Deductions section ────────────────────────────────────────────────────

    if exemptions["exemptions"]:
        section_header4 = Table(
            [[Paragraph("🔖  Deductions & Exemptions", section_style)]],
            colWidths=[6.5 * inch]
        )
        section_header4.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#333333")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(section_header4)
        elements.append(Spacer(1, 0.05 * inch))

        ded_data = [["Section", "Description", "Amount Claimed"]]
        for ex in exemptions["exemptions"]:
            ded_data.append([
                ex["section"],
                ex["description"],
                f"₹{ex['claimed']:,.0f}"
            ])
        ded_data.append(["", "TOTAL DEDUCTIONS", f"₹{exemptions['total_deductions']:,.0f}"])

        ded_table = Table(ded_data, colWidths=[1.2 * inch, 3.8 * inch, 1.5 * inch])
        ded_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUND", (0, 1), (-1, -2), [WHITE, LIGHT_GRAY]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f5e9")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))

        elements.append(ded_table)
        elements.append(Spacer(1, 0.15 * inch))

    # ── ITR form section ──────────────────────────────────────────────────────

    itr = results["itr_form"]
    itr_data = [
        ["ITR Form", itr["recommended_form"]],
        ["Reason", itr["reason"]],
        ["Filing Deadline", itr["filing_deadline"]],
        ["Late Fee", itr["late_fee"]],
    ]

    section_header5 = Table(
        [[Paragraph("📝  ITR Filing Information", section_style)]],
        colWidths=[6.5 * inch]
    )
    section_header5.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(section_header5)
    elements.append(Spacer(1, 0.05 * inch))

    itr_table = Table(itr_data, colWidths=[2.5 * inch, 4 * inch])
    itr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUND", (1, 0), (1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(itr_table)
    elements.append(Spacer(1, 0.3 * inch))

    # ── Disclaimer ────────────────────────────────────────────────────────────

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd")))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(
        "⚠️ DISCLAIMER: This report is generated by AaykarAI for informational purposes only. "
        "It is not a substitute for professional tax advice. Please consult a Chartered Accountant "
        "before filing your Income Tax Return. Tax laws are subject to change.",
        disclaimer_style
    ))

    # ── Build PDF ─────────────────────────────────────────────────────────────

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()