# services/pdf_service.py

from pypdf import PdfReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter

import os


# ── Colour palette ──────────────────────────────────────────────────────────────
ACCENT     = colors.HexColor("#1A56DB")   # section heading colour
BLACK      = colors.HexColor("#111827")
GRAY       = colors.HexColor("#6B7280")
LIGHT_GRAY = colors.HexColor("#D1D5DB")


def _build_styles():
    """Return a dict of named ParagraphStyles for the resume."""
    base = dict(
        fontName="Helvetica",
        textColor=BLACK,
        leading=13,
    )

    return {
        "name": ParagraphStyle(
            "ResumeName",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=BLACK,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=12,
        ),
        "section_heading": ParagraphStyle(
            "ResumeSectionHeading",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=ACCENT,
            spaceBefore=10,
            spaceAfter=2,
            leading=14,
            textTransform="uppercase",
        ),
        "summary": ParagraphStyle(
            "ResumeSummary",
            fontName="Helvetica",
            fontSize=9,
            textColor=BLACK,
            leading=13,
            spaceAfter=4,
        ),
        "entry_title": ParagraphStyle(
            "ResumeEntryTitle",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=BLACK,
            leading=13,
            spaceAfter=0,
        ),
        "entry_sub": ParagraphStyle(
            "ResumeEntrySub",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=GRAY,
            leading=12,
            spaceAfter=1,
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            fontName="Helvetica",
            fontSize=9,
            textColor=BLACK,
            leading=13,
            leftIndent=14,
            bulletIndent=4,
            spaceAfter=1,
        ),
        "skill_line": ParagraphStyle(
            "ResumeSkillLine",
            fontName="Helvetica",
            fontSize=9,
            textColor=BLACK,
            leading=13,
            spaceAfter=1,
        ),
    }


def _section_rule(elements):
    """Append a thin accent-coloured horizontal rule."""
    elements.append(HRFlowable(
        width="100%", thickness=0.8,
        color=ACCENT, spaceAfter=4, spaceBefore=2,
    ))


def _bullet_items(text_or_list, styles):
    """Convert a string or list into ReportLab bullet ListItems."""
    items = []
    if isinstance(text_or_list, str):
        # Split on newlines or semicolons for multi-point descriptions
        lines = [l.strip(" •–-") for l in text_or_list.replace(";", "\n").splitlines() if l.strip()]
    elif isinstance(text_or_list, list):
        lines = [str(l).strip(" •–-") for l in text_or_list if str(l).strip()]
    else:
        lines = []

    for line in lines:
        if line:
            items.append(ListItem(Paragraph(line, styles["bullet"]),
                                  bulletColor=ACCENT, leftIndent=16, bulletIndent=6))
    return items


class PDFService:

    @staticmethod
    def extract_text_from_pdf(file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    @staticmethod
    def generate_resume_pdf(resume_json: dict, output_path: str):
        """
        Generate a professionally structured, ATS-friendly single-column resume PDF.
        Sections preserved: Name/Contact → Summary → Skills → Experience → Projects → Education
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=0.65 * inch,
            rightMargin=0.65 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.55 * inch,
        )

        S = _build_styles()
        elements = []

        # ── NAME ──────────────────────────────────────────────────────────────
        name = resume_json.get("name", "Your Name")
        elements.append(Paragraph(name, S["name"]))

        # ── CONTACT INFO ─────────────────────────────────────────────────────
        contact = resume_json.get("contact_info", {})
        contact_parts = []
        for key in ("email", "phone", "linkedin", "github", "location"):
            val = contact.get(key, "").strip()
            if val:
                contact_parts.append(val)
        if contact_parts:
            elements.append(Paragraph("  |  ".join(contact_parts), S["contact"]))

        elements.append(Spacer(1, 0.08 * inch))

        # ── SUMMARY ───────────────────────────────────────────────────────────
        summary = resume_json.get("summary", "").strip()
        if summary:
            elements.append(Paragraph("Professional Summary", S["section_heading"]))
            _section_rule(elements)
            elements.append(Paragraph(summary, S["summary"]))
            elements.append(Spacer(1, 0.05 * inch))

        # ── SKILLS ────────────────────────────────────────────────────────────
        skills = resume_json.get("skills", [])
        if skills:
            elements.append(Paragraph("Skills", S["section_heading"]))
            _section_rule(elements)

            if isinstance(skills, dict):
                # skills is a dict of categories → list
                for category, skill_list in skills.items():
                    joined = ", ".join(skill_list) if isinstance(skill_list, list) else str(skill_list)
                    elements.append(Paragraph(f"<b>{category}:</b> {joined}", S["skill_line"]))
            else:
                # flat list — group into one comma-separated line for readability,
                # break every ~7 skills onto a new line
                skill_strs = [str(s).strip() for s in skills if str(s).strip()]
                chunk_size = 7
                for i in range(0, len(skill_strs), chunk_size):
                    chunk = skill_strs[i:i + chunk_size]
                    elements.append(Paragraph("  •  ".join(chunk), S["skill_line"]))

            elements.append(Spacer(1, 0.05 * inch))

        # ── EXPERIENCE ────────────────────────────────────────────────────────
        experience = resume_json.get("experience", [])
        if experience:
            elements.append(Paragraph("Experience", S["section_heading"]))
            _section_rule(elements)

            for exp in experience:
                if not isinstance(exp, dict):
                    elements.append(Paragraph(str(exp), S["bullet"]))
                    continue

                title    = exp.get("title", exp.get("role", "")).strip()
                company  = exp.get("company", exp.get("organization", "")).strip()
                duration = exp.get("duration", exp.get("dates", exp.get("date", ""))).strip()
                location = exp.get("location", "").strip()
                desc     = exp.get("description", exp.get("responsibilities", exp.get("details", "")))

                # Title line
                title_text = f"<b>{title}</b>" if title else ""
                if company:
                    title_text += f" — {company}"
                if title_text:
                    elements.append(Paragraph(title_text, S["entry_title"]))

                # Sub-line: duration / location
                sub_parts = [p for p in [duration, location] if p]
                if sub_parts:
                    elements.append(Paragraph(" | ".join(sub_parts), S["entry_sub"]))

                # Description bullets
                bullet_items = _bullet_items(desc, S)
                if bullet_items:
                    elements.append(ListFlowable(bullet_items, bulletType="bullet",
                                                 leftIndent=10, bulletFontSize=7,
                                                 bulletColor=ACCENT, spaceAfter=2))

                elements.append(Spacer(1, 0.08 * inch))

        # ── PROJECTS ──────────────────────────────────────────────────────────
        projects = resume_json.get("projects", [])
        if projects:
            elements.append(Paragraph("Projects", S["section_heading"]))
            _section_rule(elements)

            for proj in projects:
                if not isinstance(proj, dict):
                    elements.append(Paragraph(str(proj), S["bullet"]))
                    continue

                title       = proj.get("title", proj.get("name", "")).strip()
                tech        = proj.get("technologies", proj.get("tech_stack", proj.get("stack", ""))).strip() \
                              if isinstance(proj.get("technologies", proj.get("tech_stack", proj.get("stack", ""))), str) \
                              else ", ".join(proj.get("technologies", proj.get("tech_stack", proj.get("stack", []))))
                duration    = proj.get("duration", proj.get("dates", proj.get("date", ""))).strip() \
                              if isinstance(proj.get("duration", proj.get("dates", proj.get("date", ""))), str) else ""
                desc        = proj.get("description", proj.get("details", ""))

                title_text = f"<b>{title}</b>" if title else ""
                if tech:
                    title_text += f" <font color='#{GRAY.hexval()[2:]}'>[{tech}]</font>"
                if title_text:
                    elements.append(Paragraph(title_text, S["entry_title"]))
                if duration:
                    elements.append(Paragraph(duration, S["entry_sub"]))

                bullet_items = _bullet_items(desc, S)
                if bullet_items:
                    elements.append(ListFlowable(bullet_items, bulletType="bullet",
                                                 leftIndent=10, bulletFontSize=7,
                                                 bulletColor=ACCENT, spaceAfter=2))

                elements.append(Spacer(1, 0.08 * inch))

        # ── EDUCATION ─────────────────────────────────────────────────────────
        education = resume_json.get("education", [])
        if education:
            elements.append(Paragraph("Education", S["section_heading"]))
            _section_rule(elements)

            for ed in education:
                if not isinstance(ed, dict):
                    elements.append(Paragraph(str(ed), S["bullet"]))
                    continue

                degree   = ed.get("degree", ed.get("title", ed.get("qualification", ""))).strip()
                school   = ed.get("school", ed.get("institution", ed.get("university", ""))).strip()
                year     = ed.get("year", ed.get("duration", ed.get("dates", ""))).strip() \
                           if isinstance(ed.get("year", ed.get("duration", ed.get("dates", ""))), str) else ""
                gpa      = ed.get("gpa", ed.get("cgpa", ed.get("grade", ""))).strip() \
                           if isinstance(ed.get("gpa", ed.get("cgpa", ed.get("grade", ""))), str) else ""

                title_parts = []
                if degree:
                    title_parts.append(f"<b>{degree}</b>")
                if school:
                    title_parts.append(school)
                if title_parts:
                    elements.append(Paragraph(" — ".join(title_parts), S["entry_title"]))

                sub_parts = [p for p in [year, (f"GPA: {gpa}" if gpa else "")] if p]
                if sub_parts:
                    elements.append(Paragraph(" | ".join(sub_parts), S["entry_sub"]))

                elements.append(Spacer(1, 0.07 * inch))

        # ── CERTIFICATIONS (optional key) ─────────────────────────────────────
        certs = resume_json.get("certifications", resume_json.get("certificates", []))
        if certs:
            elements.append(Paragraph("Certifications", S["section_heading"]))
            _section_rule(elements)
            for cert in certs:
                if isinstance(cert, dict):
                    name = cert.get("name", cert.get("title", "")).strip()
                    issuer = cert.get("issuer", cert.get("organization", "")).strip()
                    year   = cert.get("year", cert.get("date", "")).strip() \
                             if isinstance(cert.get("year", cert.get("date", "")), str) else ""
                    line = f"<b>{name}</b>" if name else ""
                    if issuer:
                        line += f" — {issuer}"
                    if year:
                        line += f" ({year})"
                    elements.append(Paragraph(line, S["entry_title"]))
                else:
                    elements.append(Paragraph(str(cert), S["bullet"]))
                elements.append(Spacer(1, 0.04 * inch))

        doc.build(elements)