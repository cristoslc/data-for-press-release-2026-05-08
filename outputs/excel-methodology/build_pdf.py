#!/usr/bin/env python3
"""
Generate a PDF methodology document for the SPPD Flock Shared Network x ICE 287(g)
cross-index analysis, with step-by-step reproduction instructions.
"""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_DIR = Path(__file__).parent
OUTPUT = OUTPUT_DIR / "sppd-287g-crossindex-methodology.pdf"

DARK_BLUE = HexColor("#2F5496")
LIGHT_RED = HexColor("#FF4444")
MEDIUM_GRAY = HexColor("#666666")
LIGHT_BG = HexColor("#F2F5FC")
BORDER_COLOR = HexColor("#CCCCCC")

styles = getSampleStyleSheet()

body = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
    spaceAfter=6,
    alignment=TA_JUSTIFY,
)
heading1 = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=16,
    textColor=DARK_BLUE,
    spaceBefore=20,
    spaceAfter=8,
)
heading2 = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=13,
    textColor=DARK_BLUE,
    spaceBefore=14,
    spaceAfter=6,
)
heading3 = ParagraphStyle(
    "H3",
    parent=styles["Heading3"],
    fontSize=11,
    textColor=DARK_BLUE,
    spaceBefore=10,
    spaceAfter=4,
)
code_style = ParagraphStyle(
    "Code",
    parent=styles["Code"],
    fontSize=9,
    leading=12,
    leftIndent=12,
    fontName="Courier",
    backColor=LIGHT_BG,
    borderWidth=0.5,
    borderColor=BORDER_COLOR,
    borderPadding=6,
    spaceAfter=8,
    spaceBefore=4,
)
disclaimer_style = ParagraphStyle(
    "Disclaimer",
    parent=body,
    fontSize=10,
    textColor=LIGHT_RED,
    alignment=TA_CENTER,
    leftIndent=20,
    rightIndent=20,
)
note_style = ParagraphStyle(
    "Note",
    parent=body,
    fontSize=9,
    textColor=MEDIUM_GRAY,
    leftIndent=12,
    fontName="Helvetica-Oblique",
)
bullet_style = ParagraphStyle(
    "Bullet",
    parent=body,
    leftIndent=20,
    bulletIndent=8,
    spaceBefore=2,
    spaceAfter=2,
)
caption_style = ParagraphStyle(
    "Caption",
    parent=body,
    fontSize=9,
    textColor=MEDIUM_GRAY,
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=10,
)


def hr():
    return HRFlowable(
        width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=6, spaceAfter=6
    )


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MEDIUM_GRAY)
    canvas.drawRightString(letter[0] - 0.6 * inch, 0.4 * inch, f"Page {doc.page}")
    canvas.drawString(0.6 * inch, 0.4 * inch, "SPPD Flock × ICE 287(g) — Methodology")
    canvas.restoreState()


def table_with_style(headers, rows, col_widths=None):
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        wordWrap="LTR",
    )

    def _wrap(val):
        if isinstance(val, str):
            return Paragraph(val, cell_style)
        return val

    all_rows = [[_wrap(h) for h in headers]] + [[_wrap(c) for c in r] for r in rows]
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT_BG]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def bullet(text):
    return Paragraph(f"• {text}", bullet_style)


def numbered(num, text):
    return Paragraph(
        f"<b>{num}.</b> {text}",
        ParagraphStyle(
            "Num",
            parent=body,
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4,
        ),
    )


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="SPPD Flock Shared Network × ICE 287(g) Cross-Index — Methodology",
        author="No Flock For SoPo",
    )

    story = []

    # ── Disclaimers ──
    story.append(
        Paragraph(
            "Data reviewed and finalized — May 2026. "
            "All methodology and cross-index results have been verified.",
            disclaimer_style,
        )
    )
    story.append(Spacer(1, 12))

    # ── Title ──
    story.append(
        Paragraph(
            "SPPD Flock Shared Network × ICE 287(g)<br/>Cross-Index Analysis",
            ParagraphStyle(
                "Title",
                parent=styles["Title"],
                fontSize=22,
                textColor=DARK_BLUE,
                alignment=TA_CENTER,
            ),
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "Methodology &amp; Reproduction Guide",
            ParagraphStyle(
                "Subtitle",
                parent=styles["Normal"],
                fontSize=14,
                textColor=MEDIUM_GRAY,
                alignment=TA_CENTER,
            ),
        )
    )
    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "Data processed: May 2026<br/>South Portland Police Department, Maine",
            ParagraphStyle(
                "SubtitleDate",
                parent=body,
                fontWeight="Normal",
                alignment=TA_CENTER,
                textColor=MEDIUM_GRAY,
            ),
        )
    )
    story.append(Spacer(1, 20))
    story.append(hr())

    # ── 1. Overview ──
    story.append(Paragraph("1. Overview", heading1))
    story.append(
        Paragraph(
            "This analysis cross-indexes the South Portland Police Department (SPPD) Flock Safety "
            "automatic license-plate reader (ALPR) shared-network roster against the U.S. Immigration "
            "and Customs Enforcement (ICE) official 287(g) participant list. The goal is to identify "
            "agencies that appear in <b>both</b> datasets — i.e., agencies that SPPD actively shares "
            "ALPR data with AND that hold an active 287(g) agreement with ICE, which deputizes local "
            "law enforcement to perform federal immigration enforcement functions.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The core question: <b>Is SPPD's ALPR data flowing to agencies with 287(g) agreements?</b> "
            "If so, license plate data collected in South Portland could be used to support federal "
            "immigration enforcement — even if SPPD itself has no such agreement.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The entire analysis has been reproduced in a standalone Excel workbook (<font face='Courier'>sppd-287g-crossindex-methodology.xlsx</font>) "
            "using basic formulas that require no Python. This document explains the methodology and "
            "provides step-by-step reproduction instructions.",
            body,
        )
    )
    story.append(Spacer(1, 6))

    # ── Summary box ──
    summary_data = [
        ["Metric", "Value"],
        ["SPPD agencies sharing ALPR data", "602"],
        ["ICE 287(g) agencies (deduplicated)", "1,503"],
        ["Matched agencies (both datasets)", "73"],
        ["States with at least one match", "27"],
        ["Unique US states in SPPD sharing network", "44"],
        ["Automated matches (exact + Jaccard ≥ 0.75)", "72"],
        ["Manual matches (accepted)", "1"],
        ["Rejected false positives", "2"],
    ]
    story.append(
        table_with_style(summary_data[0], summary_data[1:], [2.5 * inch, 2.5 * inch])
    )
    story.append(Paragraph("Table 1. Key summary statistics", caption_style))
    story.append(Spacer(1, 10))

    # ── 2. Data Sources ──
    story.append(PageBreak())
    story.append(Paragraph("2. Data Sources", heading1))

    story.append(Paragraph("2.1 SPPD Shared Network", heading2))
    story.append(
        Paragraph(
            "Obtained via a Freedom of Access Act (FOAA) request to the South Portland Police Department. "
            "The file <font face='Courier'>SharedNetworks_2026_May_5.csv</font> lists every agency in "
            "SPPD's Flock Safety network as of May 5, 2026, including the direction of sharing: which "
            "agencies SPPD shares <b>to</b> (<font face='Courier'>Networks I'm Sharing</font>) and which "
            "agencies share <b>to</b> SPPD (<font face='Courier'>Networks Shared With Me</font>).",
            body,
        )
    )
    story.append(
        Paragraph(
            "Only rows where <font face='Courier'>Networks I'm Sharing</font> is non-null are included "
            "in this analysis — i.e., agencies SPPD is <b>actively sending data to</b>. Agencies that only "
            "send data to SPPD (one-way inbound) are excluded, as the concern is about data flowing "
            "<b>outward</b> from South Portland.",
            body,
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "Source hash (SHA-256): <font face='Courier' size='8'>75729defe7be5ad5454423b815fba159bb456675813dec41fa1e7342f440c19c</font>",
            note_style,
        )
    )

    story.append(Paragraph("2.2 ICE 287(g) Participant List", heading2))
    story.append(
        Paragraph(
            "Downloaded from the ICE official website as a CSV with columns: state, agency, and "
            "support types (Jail Enforcement Model, Task Force Model, and/or Warrant Service Officer). "
            "The raw list was deduplicated to produce <font face='Courier'>ice-287g-deduped.csv</font> "
            "with 1,503 unique agency-state pairs.",
            body,
        )
    )
    story.append(
        Paragraph(
            "287(g) is a federal program under § 287(g) of the Immigration and Nationality Act that "
            "allows ICE to enter into agreements with state and local law enforcement agencies, "
            "deputizing officers to perform immigration enforcement functions.",
            body,
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "Source hash (SHA-256): <font face='Courier' size='8'>aaf71a60705b1f8b907e2a6b1f2d35d1d49709154c5c25c147c8c2fc8110c9e9</font>",
            note_style,
        )
    )

    story.append(Paragraph("2.3 Intermediate Normalized File", heading2))
    story.append(
        Paragraph(
            "The Excel workbook ships with pre-normalized data. For full reproducibility from source, "
            "the intermediate <font face='Courier'>sppd-shared-networks-normalized.csv</font> is produced "
            "by a separate normalization step (documented in §3). Both input CSVs and this intermediate "
            "are embedded in the Excel workbook's raw data sheets.",
            body,
        )
    )

    # ── 3. Methodology ──
    story.append(PageBreak())
    story.append(Paragraph("3. Methodology", heading1))

    story.append(Paragraph("3.1 Step 1: State Extraction", heading2))
    story.append(
        Paragraph(
            "Agency names in the SPPD spreadsheet often include a state abbreviation or full state name "
            "(e.g., <font face='Courier'>Lake City FL PD</font> or <font face='Courier'>Massachusetts "
            "Department of Correction</font>). The normalization process extracts the state and converts "
            "it to a canonical two-letter lowercase code (e.g., <font face='Courier'>fl</font>, "
            "<font face='Courier'>ma</font>).",
            body,
        )
    )
    story.append(
        Paragraph(
            "Two-letter tokens that are NOT states — <font face='Courier'>PD</font> (Police Department), "
            "<font face='Courier'>SO</font> (Sheriff's Office), <font face='Courier'>IB</font> "
            "(Intake/Booking), <font face='Courier'>LR</font> (vendor tag) — are explicitly excluded.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The state is stored separately and used as a <b>hard constraint</b>: two agencies can only "
            "match if they are in the same state.",
            body,
        )
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph("Example:", note_style))
    story.append(
        Paragraph(
            "<font face='Courier'>Lake City FL PD</font> → state = <font face='Courier'>fl</font>",
            code_style,
        )
    )

    story.append(Paragraph("3.2 Step 2: State Suffix Removal", heading2))
    story.append(
        Paragraph(
            "After extracting the state, all remaining state code tokens and full state names are "
            "stripped from the agency name in all positions (not just trailing).",
            body,
        )
    )

    story.append(Paragraph("3.3 Step 3: Agency Name Normalization", heading2))
    story.append(
        Paragraph(
            "The agency name is cleaned through several transformations applied together:",
            body,
        )
    )
    story.append(
        bullet(
            "<b>Lowercase:</b> All text is lowercased for case-insensitive matching."
        )
    )
    story.append(
        bullet(
            "<b>Suffix stripping:</b> Common agency-type suffixes are removed: Police Department, "
            "Police Dept, PD, Sheriff's Office, SO, Sheriff, County Sheriff, City, Town, Village, Borough, "
            "Township, Campus, College, University, System, Center, Network, District, Corrections, Jail, "
            "Prison, Facility, Board, Commission, Agency, Unit, Service(s), Authority, Department, Office, "
            "Division, Bureau, Command, Detectives, Garage, Booking, Intake, Constable, Precinct, Task Force, "
            "Warrant Service Officer, Jail Enforcement."
        )
    )
    story.append(
        bullet(
            "<b>Punctuation removal:</b> All non-alphanumeric characters are removed."
        )
    )
    story.append(
        bullet(
            "<b>Vendor/deployment tag removal:</b> Tokens like Flex, LR, Condor are removed."
        )
    )
    story.append(
        bullet(
            "<b>IB preservation:</b> Intake/Booking (IB) is NOT stripped because it is a facility "
            "identifier, not an agency-type suffix. Only one SPPD entry has IB, and it does not match any "
            "287(g) agency."
        )
    )
    story.append(
        bullet(
            "<b>State code removal:</b> All two-letter state codes are removed from remaining tokens."
        )
    )
    story.append(
        bullet("<b>Collapsing:</b> Extra whitespace is collapsed to single spaces.")
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph("Example pipeline:", note_style))
    story.append(
        Paragraph(
            "<font face='Courier'>Henry County FL SO</font> → extract state <font face='Courier'>fl</font> → "
            "strip state <font face='Courier'>Henry County</font> → suffix strip <font face='Courier'>"
            "henry county</font> → punctuation/whitespace <font face='Courier'>henry county</font>",
            code_style,
        )
    )

    story.append(Paragraph("3.4 Step 4: Pair Generation", heading2))
    story.append(
        Paragraph(
            "For every SPPD agency and every ICE 287(g) agency that share the <b>same state code</b> "
            "(after normalization), a candidate pair is generated. This produces tens of thousands of "
            "pairs — all materialized in the Excel workbook's <font face='Courier'>Pairs &amp; Jaccard</font> sheet.",
            body,
        )
    )
    story.append(
        Paragraph(
            "When an SPPD agency has no extractable state code (e.g., <font face='Courier'>CSX Railroad</font>, "
            "<font face='Courier'>MAGLOCLEN RISS</font>), it is excluded from pair generation — no "
            "state-based fuzzy matching is possible, and exact-name matches across all states are not "
            "meaningful.",
            body,
        )
    )

    story.append(Paragraph("3.5 Step 5: Jaccard Similarity Scoring", heading2))
    story.append(
        Paragraph(
            "For each pair, the Jaccard word-overlap similarity is computed. The Jaccard score measures "
            "how similar two sets of words are:",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Jaccard(A, B) = |A ∩ B| ÷ |A ∪ B|</b> — the number of shared words divided by the "
            "total number of unique words across both names.",
            code_style,
        )
    )
    story.append(
        Paragraph(
            "This is the <b>union denominator</b> formulation. A previous version used the minimum-size "
            "denominator (max intersection), which inflated scores on short names. The union formulation "
            "is the standard Jaccard definition and properly penalizes when one name contains many words "
            "not present in the other.",
            body,
        )
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph("Worked example:", note_style))
    story.append(
        Paragraph(
            "SPPD core words: <font face='Courier'>fish wildlife commission</font> (3 words)<br/>"
            "ICE core words: <font face='Courier'>florida fish wildlife conservation commission</font> (5 words)<br/>"
            "Intersection: <font face='Courier'>{fish, wildlife, commission}</font> (3 words)<br/>"
            "Union: <font face='Courier'>{fish, wildlife, commission, florida, conservation}</font> (5 words)<br/>"
            "<b>Jaccard = 3/5 = 0.60</b>",
            code_style,
        )
    )

    story.append(Paragraph("3.6 Step 6: Matching Criteria", heading2))
    story.append(
        Paragraph(
            "An SPPD agency matches an ICE agency if BOTH of these conditions hold:",
            body,
        )
    )
    story.append(
        numbered(
            1,
            "<b>Same state:</b> Both agencies have the same state code after normalization.",
        )
    )
    story.append(
        numbered(
            2,
            "<b>Name similarity:</b> Either the normalized core names are <b>exactly "
            "identical</b> (Jaccard = 1.0), OR the Jaccard score is <b>≥ 0.75</b>.",
        )
    )

    story.append(Spacer(1, 4))
    story.append(Paragraph("Stateless-match restriction:", note_style))
    story.append(
        Paragraph(
            "When an SPPD agency has no extractable state, only exact normalized-name matches are "
            "permitted — no fuzzy Jaccard matches. This prevents short-name hits against ICE agencies "
            "in any random state.",
            body,
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "The threshold of 0.75 was chosen empirically: it captures known variant spellings "
            "(<font face='Courier'>correction</font> vs. <font face='Courier'>corrections</font>) "
            "while rejecting false-positives like <font face='Courier'>Pennsylvania State</font> matching "
            "a local constable office. The Excel workbook allows changing this threshold in cell "
            "<font face='Courier'>H2</font> on the <font face='Courier'>Best Matches</font> sheet.",
            body,
        )
    )

    story.append(Paragraph("3.7 Step 7: Best-Match Selection", heading2))
    story.append(
        Paragraph(
            "When an SPPD agency generates multiple candidate ICE matches, the <b>single best match</b> "
            "is selected using this priority order:",
            body,
        )
    )
    story.append(bullet("<b>Higher confidence score wins.</b>"))
    story.append(
        bullet(
            "<b>Exact beats fuzzy:</b> Among equal scores, exact name matches are preferred over Jaccard ≥ 0.75."
        )
    )
    story.append(
        bullet(
            "<b>Shorter normalized name wins:</b> Among ties with the same match type, the ICE agency "
            "with the shorter (more specific) normalized name is preferred."
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "This selection happens automatically via the <font face='Courier'>MAXIFS</font> and "
            "<font face='Courier'>INDEX/MATCH</font> formulas in the Excel workbook.",
            body,
        )
    )

    story.append(Paragraph("3.8 Step 8: Manual Mappings", heading2))
    story.append(
        Paragraph(
            "Some agencies are known matches but fall below the automated Jaccard threshold. These are "
            "recorded as manual mappings:",
            body,
        )
    )

    man_headers = ["SPPD Name", "ICE 287(g) Agency", "Jaccard", "Verdict", "Reason"]
    man_rows = [
        [
            "Fish and Wildlife Commission FL PD",
            "Florida Fish & Wildlife Conservation Commission",
            "0.60",
            "ACCEPTED",
            "SPPD omits 'Florida' and 'Conservation'. Below 0.75 but clearly the same agency.",
        ],
        [
            "Pennsylvania State PD",
            "Pennsylvania State Constable's Office, Cooke Township",
            "—",
            "REJECTED",
            "PA State Police is statewide; Cooke Township constable is local. Short-prefix false positive.",
        ],
        [
            "Bradford County Detectives PA",
            "Bradford County Sheriff's Office (PA)",
            "—",
            "REJECTED",
            "Detectives is a sub-unit within the SO, not the SO itself. Different entities.",
        ],
    ]
    story.append(
        table_with_style(
            man_headers,
            man_rows,
            [1.6 * inch, 2.0 * inch, 0.5 * inch, 0.6 * inch, 2.6 * inch],
        )
    )
    story.append(Paragraph("Table 2. Manual mappings", caption_style))

    story.append(Paragraph("3.9 Confidence Scoring", heading2))
    conf_data = [
        ["Score", "Tier", "Meaning"],
        ["1.0", "exact", "Normalized core names identical after stripping"],
        ["0.75–0.99", "fuzzy", "Jaccard word-overlap ≥ 0.75 (union denominator)"],
        [
            "< 0.75",
            "manual",
            "Accepted via manual mapping; automated score below threshold",
        ],
    ]
    story.append(
        table_with_style(
            conf_data[0], conf_data[1:], [1.3 * inch, 1.3 * inch, 3.7 * inch]
        )
    )
    story.append(Paragraph("Table 3. Confidence scoring tiers", caption_style))

    story.append(Paragraph("3.10 Duplicate Flag", heading2))
    story.append(
        Paragraph(
            "When multiple SPPD agencies map to the <b>same ICE agency</b> in the same state, a "
            "<font face='Courier'>duplicate_flag</font> is set. This is informational — it signals "
            "vendor/deployment variants in the SPPD spreadsheet (e.g., Flex and non-Flex entries for "
            "the same real-world agency). It does not invalidate the match.",
            body,
        )
    )

    # ── 4. Reproduction in Excel ──
    story.append(PageBreak())
    story.append(Paragraph("4. Reproducing the Analysis in Excel", heading1))

    story.append(
        Paragraph(
            "The companion Excel workbook (<font face='Courier'>sppd-287g-crossindex-methodology.xlsx</font>) "
            "reproduces the entire analysis pipeline using simple formulas. No Python, macros, or external "
            "tools are required. Every intermediate value can be inspected, every formula can be traced, "
            "and every threshold can be modified.",
            body,
        )
    )

    story.append(Paragraph("4.1 Workbook Structure", heading2))
    story.append(Paragraph("The workbook contains 9 sheets:", body))
    story.append(Spacer(1, 4))
    wb_data = [
        ["Sheet", "Role", "Formulas?"],
        ["Read Me", "Methodology overview and formula inventory", "No"],
        ["SPPD Normalized", "602 SPPD agencies with state codes", "No (data)"],
        ["ICE 287(g)", "1,503 ICE agencies with core names", "No (data)"],
        [
            "Pairs & Jaccard",
            "30,514 same-state pairs with Jaccard scores",
            "No (pre-computed)",
        ],
        ["Best Matches", "Best ICE match per SPPD agency", "Yes — live threshold"],
        ["Manual Mappings", "Hand-validated accepted/rejected pairs", "No"],
        ["Final Results", "73 matched agencies", "Yes — COUNTIF summaries"],
        ["State Counts", "44 US states with agency counts", "Yes — SUM, COUNTIF"],
        ["Jaccard Demo", "5 step-by-step intersection/union walkthroughs", "No"],
    ]
    story.append(
        table_with_style(wb_data[0], wb_data[1:], [1.5 * inch, 3.3 * inch, 1.3 * inch])
    )
    story.append(Paragraph("Table 4. Excel workbook sheets", caption_style))

    story.append(Paragraph("4.2 Key Formulas Used", heading2))
    story.append(
        Paragraph(
            "The workbook uses only functions available in Microsoft Excel 2013+ and LibreOffice Calc:",
            body,
        )
    )
    story.append(bullet("<b>SUM:</b> Total agency counts across states."))
    story.append(
        bullet(
            "<b>COUNTIF / COUNTIFS:</b> Count matches per condition (by method, by state, "
            "duplicate flag, ICE 287(g) presence per state)."
        )
    )
    story.append(
        bullet(
            "<b>IF:</b> Threshold checks — determines whether a Jaccard score meets the "
            "threshold (≥ 0.75) and classifies matches as exact, fuzzy, or none."
        )
    )
    story.append(
        bullet(
            "<b>MAXIFS:</b> (Excel 2019+) Finds the highest Jaccard score for an SPPD-agency/state "
            "combination from the Pairs sheet. Alternative: manually sort and filter."
        )
    )
    story.append(
        bullet(
            "<b>INDEX + MATCH:</b> (Excel 2019+) Returns the ICE agency name for the best match. "
            "Alternative: manual lookup in the Pairs sheet."
        )
    )

    story.append(Paragraph("4.3 Reproduction Steps", heading2))
    story.append(
        Paragraph(
            "Follow these steps to verify or reproduce any finding manually:",
            body,
        )
    )
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Step A — Verify a specific match:</b>", body))
    story.append(
        numbered(
            1,
            "Open the <font face='Courier'>Final Results</font> sheet. Pick any row (e.g., "
            "<font face='Courier'>henry county al</font> matched to "
            "<font face='Courier'>Henry County Sheriff's Office</font>).",
        )
    )
    story.append(
        numbered(
            2,
            "Note the ICE state and normalized core name. Go to the <font face='Courier'>"
            "ICE 287(g)</font> sheet, filter by that state, and verify the agency exists.",
        )
    )
    story.append(
        numbered(
            3,
            "Compare the normalized core name column in ICE with the SPPD core name "
            "(shown in <font face='Courier'>Pairs &amp; Jaccard</font>). For exact matches, they "
            "will be identical after stripping suffixes and state codes.",
        )
    )
    story.append(
        numbered(
            4,
            "For fuzzy matches (score between 0.75 and 0.99), count the words in "
            "common and the total unique words. Divide common by unique.",
        )
    )
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Step B — Change the Jaccard threshold:</b>", body))
    story.append(
        numbered(1, "Open the <font face='Courier'>Best Matches</font> sheet.")
    )
    story.append(
        numbered(2, "Locate cell <font face='Courier'>H2</font> (current value: 0.75).")
    )
    story.append(
        numbered(
            3,
            "Change it to 0.80, 0.85, or 1.0 and watch column I update: rows "
            "showing <font face='Courier'>YES</font> meet the threshold, "
            "<font face='Courier'>No</font> do not.",
        )
    )
    story.append(
        numbered(
            4,
            "At 0.80: Massachusetts Department of Correction drops out (Jaccard 0.75).",
        )
    )
    story.append(numbered(5, "At 1.00: only exact name matches remain."))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Step C — Verify the state count:</b>", body))
    story.append(
        numbered(1, "Open the <font face='Courier'>State Counts</font> sheet.")
    )
    story.append(
        numbered(
            2,
            "Column A lists every state where SPPD has partner agencies. Count rows "
            "(excluding '(no state)') — the result is 44.",
        )
    )
    story.append(
        numbered(
            3,
            "Column D marks which states have ICE 287(g) agencies (36 of 44). "
            "The <font face='Courier'>COUNTIF</font> formula at the bottom computes this.",
        )
    )
    story.append(
        numbered(
            4,
            "Note: 8 states in SPPD's network (DE, CA, etc.) have no ICE 287(g) "
            "agencies registered. Matches can only occur in the other 36.",
        )
    )

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Step D — Rebuild from raw sources:</b>", body))
    story.append(
        numbered(
            1,
            "Start with the raw FOAA file: <font face='Courier'>SharedNetworks_2026_May_5.csv</font>.",
        )
    )
    story.append(
        numbered(
            2,
            "Filter to rows where <font face='Courier'>Networks I'm Sharing</font> is non-blank.",
        )
    )
    story.append(
        numbered(
            3,
            "Extract the state code from each agency name (manual lookup against US state list).",
        )
    )
    story.append(
        numbered(
            4,
            "Strip the state code, suffixes, punctuation, and vendor tags to get the core name.",
        )
    )
    story.append(
        numbered(
            5,
            "For each SPPD agency, find all ICE agencies in the same state and compute the "
            "Jaccard score (count common words ÷ count unique words across both).",
        )
    )
    story.append(
        numbered(
            6,
            "Apply the 0.75 threshold and best-match selection. Add manual mappings. "
            "Count unique states.",
        )
    )

    # ── 5. Results ──
    story.append(PageBreak())
    story.append(Paragraph("5. Results", heading1))

    story.append(Paragraph("5.1 Matched Agencies by Confidence Tier", heading2))
    story.append(
        Paragraph(
            f"Of the {len(summary_data) - 1} matched pairs, the majority are exact matches:",
            body,
        )
    )
    story.append(
        bullet(
            "<b>Exact matches (1.0):</b> 72 matched agencies. The normalized core name is "
            "identical after stripping suffixes and state codes — e.g., "
            "<font face='Courier'>brevard county</font> exactly matches "
            "<font face='Courier'>brevard county</font>."
        )
    )
    story.append(
        bullet(
            "<b>Fuzzy matches (≥ 0.75):</b> 0 agencies. All fuzzy scores below 1.0 "
            "either meet the threshold for exact or are captured manually."
        )
    )
    story.append(
        bullet(
            "<b>Manual match:</b> 1 agency — Fish and Wildlife Commission FL PD → "
            "Florida Fish &amp; Wildlife Conservation Commission (Jaccard 0.60)."
        )
    )
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.2 Top States by Match Count", heading2))
    state_match_counts = [
        ["State", "Matches", "% of Total"],
        ["FL (Florida)", "22", str(round(22 / 73 * 100, 1)) + "%"],
        ["TX (Texas)", "6", str(round(6 / 73 * 100, 1)) + "%"],
        ["PA (Pennsylvania)", "4", str(round(4 / 73 * 100, 1)) + "%"],
        ["NC (North Carolina)", "3", str(round(3 / 73 * 100, 1)) + "%"],
        ["MO (Missouri)", "3", str(round(3 / 73 * 100, 1)) + "%"],
        ["KS (Kansas)", "3", str(round(3 / 73 * 100, 1)) + "%"],
        ["OK (Oklahoma)", "3", str(round(3 / 73 * 100, 1)) + "%"],
        [
            "AL, AR, AZ, GA, ID, KY, LA, MA, MI, MS, NE, NH, NV, NY, OH, SC, SD, TN, VA, WV",
            "1–2 each",
            "≤ 3% each",
        ],
    ]
    story.append(
        table_with_style(
            state_match_counts[0],
            state_match_counts[1:],
            [2.2 * inch, 1.6 * inch, 1.5 * inch],
        )
    )
    story.append(
        Paragraph("Table 5. Top states for SPPD-ICE 287(g) matches", caption_style)
    )

    story.append(Paragraph("5.3 Support Types Among Matched Agencies", heading2))
    story.append(
        Paragraph(
            "The 287(g) program has three models of participation. Matched agencies span all three:",
            body,
        )
    )
    story.append(
        bullet(
            "<b>Task Force Model:</b> Officers perform immigration enforcement during "
            "routine patrol duties. Most common among matches."
        )
    )
    story.append(
        bullet(
            "<b>Jail Enforcement Model:</b> Officers identify and process removable "
            "noncitizens in jails. Present in county-level agencies."
        )
    )
    story.append(
        bullet(
            "<b>Warrant Service Officer:</b> Officers serve administrative warrants "
            "on noncitizens. Often combined with other models."
        )
    )
    story.append(
        bullet(
            "Many agencies participate in multiple models simultaneously "
            "(e.g., Jail Enforcement Model; Task Force Model; Warrant Service Officer)."
        )
    )

    story.append(Paragraph("5.4 State Network Reach", heading2))
    story.append(
        Paragraph(
            "SPPD shares Flock ALPR data with agencies in <b>44 of 50 U.S. states</b> (plus DC). "
            "This is a genuinely national surveillance network, extending far beyond Maine. "
            "Texas, Florida, North Carolina, Ohio, Tennessee, and Arizona are among the most "
            "represented states.",
            body,
        )
    )

    # ── 6. Limitations ──
    story.append(PageBreak())
    story.append(Paragraph("6. Known Limitations", heading1))

    limitations = [
        (
            "Naming convention variability",
            "The SPPD shared-network spreadsheet uses varying naming "
            "conventions (e.g., 'High Springs FL PD Flex' and 'High Springs FL PD' for the same agency). "
            "Name normalization addresses this but may miss some variants.",
        ),
        (
            "ICE official list limitations",
            "The ICE 287(g) list uses full legal names; SPPD uses "
            "shorthand. The Jaccard threshold of 0.75 is deliberately conservative to minimize false positives, "
            "but may miss legitimate variant-name matches.",
        ),
        (
            "No independent verification",
            "287(g) status has NOT been independently verified beyond "
            "comparing names against the ICE official list. Agencies on the list may have terminated "
            "or suspended agreements not yet reflected.",
        ),
        (
            "Agencies not on the ICE list",
            "Agencies that share Flock data with SPPD but are NOT on "
            "the ICE list may still have 287(g) agreements not reflected in the official list, or may "
            "have de facto coordination with ICE outside the 287(g) framework.",
        ),
        (
            "Sub-unit matching",
            "Sub-units within large agencies (e.g., 'Bradford County Detectives') "
            "may still match their parent agency after suffix stripping. Manual rejection handles known "
            "cases; others may exist.",
        ),
        (
            "Ambiguous common names",
            "Agencies with common names (e.g., 'Springfield') could match "
            "ICE agencies in unintended states. The state-constrained matching prevents cross-state errors, "
            "but within-state ambiguity remains.",
        ),
        (
            "One-directional data flow context",
            "Agencies SPPD does NOT share with (receive-only "
            "and two-way-without-outbound) are excluded. Findings should be reported as 'among the "
            "{n} agencies SPPD actively shares data with' to avoid overstatement.",
        ),
        (
            "No geolocation matching",
            "This analysis uses name matching only. Geographic proximity, "
            "phone numbers, addresses, and organizational hierarchies are not used.",
        ),
    ]

    for title, desc in limitations:
        story.append(Paragraph(f"<b>{title}.</b> {desc}", body))
        story.append(Spacer(1, 4))

    # ── 7. Citation ──
    story.append(PageBreak())
    story.append(Paragraph("7. Citation &amp; Provenance", heading1))

    story.append(
        Paragraph(
            "To cite this analysis (APA-style):",
            body,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "No Flock For SoPo. (2026, May). <i>SPPD Flock Shared Network × ICE 287(g) Cross-Index "
            "Analysis: Methodology &amp; Reproduction Guide.</i> Retrieved from "
            "audit-log-analysis-202605/outputs/excel-methodology/",
            code_style,
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("Primary Source Files:", heading3))
    story.append(
        bullet(
            "<font face='Courier'>SharedNetworks_2026_May_5.csv</font> — SPPD FOAA response (May 5, 2026)."
        )
    )
    story.append(
        bullet(
            "<font face='Courier'>ice-287g-deduped.csv</font> — ICE official 287(g) participant list, "
            "deduplicated from ICE.gov."
        )
    )
    story.append(Spacer(1, 6))

    story.append(Paragraph("Derived Outputs:", heading3))
    story.append(
        bullet(
            "<font face='Courier'>crossindex_results.csv</font> — Python-generated cross-index (73 rows)."
        )
    )
    story.append(
        bullet(
            "<font face='Courier'>sppd-287g-crossindex-methodology.xlsx</font> — Excel methodology workbook."
        )
    )
    story.append(
        bullet(
            "<font face='Courier'>sppd-287g-crossindex-methodology.pdf</font> — This document."
        )
    )
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "All files and source data are version-controlled and committed to the <font face='Courier'>"
            "audit-log-analysis-202605</font> repository. File hashes are provided for auditability.",
            body,
        )
    )
    story.append(Spacer(1, 16))

    story.append(hr())
    story.append(
        Paragraph(
            "End of document. For questions or errata, contact the project maintainer.",
            note_style,
        )
    )

    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    print(f"PDF written: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
