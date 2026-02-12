"""
Professional PDF Generator for Travel Itineraries
Ported from app2.py with Django enhancements
"""

import re
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


class ProfessionalPDFGenerator:
    """
    Professional PDF generator with multiple themes.
    Converts markdown-like itinerary into polished PDF with:
    - Cover page with metadata
    - Day-by-day activity tables
    - Professional styling and formatting
    - Automatic markdown cleanup
    - Multi-theme support
    """

    # Theme: Pumpkin/Orange (default)
    PUMPKIN = colors.HexColor("#f78b1f")
    PUMPKIN_DARK = colors.HexColor("#d46d00")
    INK = colors.HexColor("#111827")
    MUTED = colors.HexColor("#6b7280")
    LIGHT_BG = colors.HexColor("#fff7ed")
    BORDER = colors.HexColor("#e5e7eb")

    # Theme: Ocean Blue
    OCEAN = colors.HexColor("#0ea5e9")
    OCEAN_DARK = colors.HexColor("#0284c7")
    OCEAN_LIGHT = colors.HexColor("#e0f2fe")

    # Theme: Forest Green
    FOREST = colors.HexColor("#10b981")
    FOREST_DARK = colors.HexColor("#059669")
    FOREST_LIGHT = colors.HexColor("#d1fae5")

    @staticmethod
    def _escape(text: str) -> str:
        """Escape HTML/XML special characters"""
        if text is None:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @staticmethod
    def _strip_md(text: str) -> str:
        """Remove markdown emphasis like **bold**, *italic*, __bold__, _italic_."""
        if not text:
            return ""
        t = str(text)
        t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)  # **bold**
        t = re.sub(r"\*(.*?)\*", r"\1", t)      # *italic*
        t = re.sub(r"__(.*?)__", r"\1", t)      # __bold__
        t = re.sub(r"_(.*?)_", r"\1", t)        # _italic_
        return t

    @staticmethod
    def _is_md_table_line(line: str) -> bool:
        """Check if line is a markdown table row"""
        return "|" in line and line.strip().startswith("|")

    @staticmethod
    def _parse_md_table(lines: List[str], start_idx: int) -> Tuple[int, List[List[str]]]:
        """Parse markdown table into list of rows"""
        rows = []
        i = start_idx
        while i < len(lines):
            l = lines[i].strip()
            if not ProfessionalPDFGenerator._is_md_table_line(l):
                break
            cells = [c.strip() for c in l.strip("|").split("|")]
            # Skip separator rows (e.g., |---|---|)
            if all(set(c) <= set("-: ") for c in cells):
                i += 1
                continue
            rows.append(cells)
            i += 1
        return i, rows

    @staticmethod
    def _parse_itinerary(text: str) -> List[Tuple[str, Any]]:
        """
        Parse itinerary text into structured blocks.
        Returns list of (block_type, content) tuples.
        """
        lines = text.splitlines()
        blocks = []
        i = 0

        current_paras = []
        current_bullets = []

        def flush_paras():
            nonlocal current_paras
            if current_paras:
                blocks.append(("paragraph", "\n".join(current_paras)))
                current_paras = []

        def flush_bullets():
            nonlocal current_bullets
            if current_bullets:
                blocks.append(("bullets", current_bullets))
                current_bullets = []

        while i < len(lines):
            raw = lines[i]
            line = raw.strip()

            if not line:
                flush_paras()
                flush_bullets()
                i += 1
                continue

            # Markdown tables
            if ProfessionalPDFGenerator._is_md_table_line(line):
                flush_paras()
                flush_bullets()
                i2, rows = ProfessionalPDFGenerator._parse_md_table(lines, i)
                if rows:
                    blocks.append(("table", rows))
                i = i2
                continue

            # Day headings
            if re.match(r"^(##\s*)?Day\s+\d+[:\-\s].*", line, re.IGNORECASE):
                flush_paras()
                flush_bullets()
                blocks.append(("day_heading", line.replace("##", "").strip()))
                i += 1
                continue

            # Section headings
            if line.startswith("## "):
                flush_paras()
                flush_bullets()
                blocks.append(("heading", line.replace("## ", "").strip()))
                i += 1
                continue
            if line.startswith("# "):
                flush_paras()
                flush_bullets()
                blocks.append(("title", line.replace("# ", "").strip()))
                i += 1
                continue
            if line.startswith("### "):
                flush_paras()
                flush_bullets()
                blocks.append(("subheading", line.replace("### ", "").strip()))
                i += 1
                continue

            # Bullet points
            if line.startswith("- ") or line.startswith("* ") or line.startswith("• "):
                flush_paras()
                current_bullets.append(line.lstrip("-*• ").strip())
                i += 1
                continue

            # Time-based activity lines (e.g., "8:00 AM - Breakfast")
            if re.match(r"^\d{1,2}:\d{2}\s*[AaPp][Mm]?\s*[-–]", line):
                flush_paras()
                flush_bullets()
                blocks.append(("time_line", line))
                i += 1
                continue

            # Regular paragraph
            current_paras.append(line)
            i += 1

        flush_paras()
        flush_bullets()
        return blocks

    # Item type colors for badges
    ITEM_TYPE_COLORS = {
        'flight': '#3b82f6',      # blue
        'hotel': '#8b5cf6',       # purple
        'restaurant': '#f59e0b',  # amber
        'attraction': '#10b981',  # green
        'activity': '#06b6d4',    # cyan
        'transport': '#6366f1',   # indigo
        'note': '#6b7280',        # gray
    }

    @classmethod
    def create_itinerary_pdf(
        cls,
        itinerary_text: str,
        destination: str,
        dates: str,
        origin: str,
        budget: int,
        output_path: str,
        theme: str = "pumpkin",
        user_name: Optional[str] = None,
        include_qr: bool = False,
        qr_url: Optional[str] = None
    ) -> str:
        """
        Generate professional PDF from itinerary text.

        Args:
            itinerary_text: Markdown-formatted itinerary
            destination: Trip destination city
            dates: Date range string (e.g., "2025-12-15 to 2025-12-22")
            origin: Origin city
            budget: Trip budget in USD
            output_path: File path to save PDF
            theme: Color theme ("pumpkin", "ocean", "forest")
            user_name: Optional user name for personalization
            include_qr: Whether to include QR code
            qr_url: URL for QR code (e.g., online itinerary link)

        Returns:
            Path to generated PDF file
        """
        # Select theme colors
        if theme == "ocean":
            primary = cls.OCEAN
            primary_dark = cls.OCEAN_DARK
            light_bg = cls.OCEAN_LIGHT
        elif theme == "forest":
            primary = cls.FOREST
            primary_dark = cls.FOREST_DARK
            light_bg = cls.FOREST_LIGHT
        else:  # default pumpkin
            primary = cls.PUMPKIN
            primary_dark = cls.PUMPKIN_DARK
            light_bg = cls.LIGHT_BG

        # Create document
        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            rightMargin=0.55*inch, leftMargin=0.55*inch,
            topMargin=0.7*inch, bottomMargin=0.7*inch
        )
        styles = getSampleStyleSheet()

        # Define custom styles
        title_style = ParagraphStyle(
            "CoverTitle", parent=styles["Heading1"],
            fontSize=22, textColor=cls.INK,
            alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Bold"
        )

        subtitle_style = ParagraphStyle(
            "CoverSubtitle", parent=styles["Normal"],
            fontSize=11, textColor=cls.MUTED,
            alignment=TA_CENTER, spaceAfter=12
        )

        meta_style = ParagraphStyle(
            "Meta", parent=styles["Normal"],
            fontSize=9, textColor=cls.MUTED,
            alignment=TA_CENTER, spaceAfter=10
        )

        h2_style = ParagraphStyle(
            "H2", parent=styles["Heading2"],
            fontSize=13, textColor=primary_dark,
            spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold"
        )

        h3_style = ParagraphStyle(
            "H3", parent=styles["Heading3"],
            fontSize=11, textColor=cls.INK,
            spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold"
        )

        day_heading_style = ParagraphStyle(
            "DayHeading", parent=styles["Heading2"],
            fontSize=12, textColor=colors.white,
            spaceBefore=0, spaceAfter=0, fontName="Helvetica-Bold",
        )

        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=9, leading=13, textColor=cls.INK,
            alignment=TA_JUSTIFY, spaceAfter=4
        )

        bullet_style = ParagraphStyle(
            "Bullet", parent=body_style,
            leftIndent=14, bulletIndent=6
        )

        small_style = ParagraphStyle(
            "Small", parent=styles["Normal"],
            fontSize=8, leading=10, textColor=cls.MUTED,
            spaceAfter=2
        )

        bold_body_style = ParagraphStyle(
            "BoldBody", parent=body_style,
            fontName="Helvetica-Bold"
        )

        # Table cell style for wrapping text
        cell_style = ParagraphStyle(
            "CellStyle", parent=styles["Normal"],
            fontSize=8, leading=10, textColor=cls.INK,
        )

        cell_bold_style = ParagraphStyle(
            "CellBoldStyle", parent=cell_style,
            fontName="Helvetica-Bold",
        )

        story = []

        # ─── Cover Section ───
        story.append(Spacer(1, 10))
        story.append(Paragraph(cls._escape(destination or "Trip Itinerary"), title_style))

        if user_name:
            story.append(Paragraph(f"Prepared for {cls._escape(user_name)}", subtitle_style))

        # Metadata table (more compact, professional)
        meta_rows = [
            ["Dates", dates],
            ["Budget", f"${budget:,} USD"],
            ["Generated", datetime.now().strftime("%B %d, %Y")],
        ]

        meta_table = Table(meta_rows, colWidths=[1.2*inch, 5.8*inch])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), light_bg),
            ("TEXTCOLOR", (0,0), (-1,-1), cls.INK),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.6, cls.BORDER),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8))

        # QR Code (if requested)
        if include_qr and qr_url:
            try:
                import qrcode
                from reportlab.platypus import Image as RLImage
                from io import BytesIO

                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(qr_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                qr_image = RLImage(buffer, width=1.5*inch, height=1.5*inch)
                story.append(Paragraph("Scan for online version:", body_style))
                story.append(qr_image)
                story.append(Spacer(1, 10))
            except ImportError:
                pass  # Skip QR code if library not available

        # ─── Parse and Render Itinerary ───
        blocks = cls._parse_itinerary(itinerary_text)

        current_day_title = None
        current_day_rows = []

        def flush_day_inline():
            nonlocal current_day_title, current_day_rows
            if not current_day_title:
                return

            clean_title = cls._strip_md(current_day_title)

            # Day heading with colored banner
            day_banner_data = [[Paragraph(cls._escape(clean_title), day_heading_style)]]
            day_banner = Table(day_banner_data, colWidths=[7.0*inch], hAlign="LEFT")
            day_banner.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), primary_dark),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING", (0,0), (-1,-1), 10),
                ("ROUNDEDCORNERS", [4, 4, 0, 0]),
            ]))
            story.append(Spacer(1, 8))
            story.append(day_banner)

            if len(current_day_rows) > 1:  # Has data rows beyond header
                # Use Paragraph for wrapping in table cells
                wrapped_rows = []
                for i, row in enumerate(current_day_rows):
                    if i == 0:
                        # Header row - use bold style
                        wrapped_rows.append([
                            Paragraph(cls._escape(str(c)), cell_bold_style) for c in row
                        ])
                    else:
                        wrapped_rows.append([
                            Paragraph(cls._escape(str(c)), cell_style) for c in row
                        ])

                num_cols = len(current_day_rows[0])

                # Adjust column widths based on number of columns
                if num_cols == 5:
                    col_widths = [0.8*inch, 0.7*inch, 2.6*inch, 1.7*inch, 0.7*inch]
                elif num_cols == 2:
                    col_widths = [1.2*inch, 5.8*inch]
                else:
                    available = 7.0 * inch
                    col_widths = [available / num_cols] * num_cols

                day_tbl = Table(wrapped_rows, colWidths=col_widths, hAlign="LEFT",
                                repeatRows=1)
                day_tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), primary),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("FONTSIZE", (0,0), (-1,-1), 8),
                    ("GRID", (0,0), (-1,-1), 0.5, cls.BORDER),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, light_bg]),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("TOPPADDING", (0,0), (-1,-1), 5),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                    ("LEFTPADDING", (0,0), (-1,-1), 6),
                    ("RIGHTPADDING", (0,0), (-1,-1), 4),
                ]))
                story.append(day_tbl)
            story.append(Spacer(1, 6))

            current_day_title = None
            current_day_rows = []

        for btype, content in blocks:

            # Flush day table before starting new section
            if current_day_title and btype in ("heading", "subheading", "title"):
                flush_day_inline()

            if btype == "day_heading":
                flush_day_inline()
                current_day_title = content
                current_day_rows = [["Time", "Activity"]]
                continue

            # Tables within a day context get absorbed
            if btype == "table" and current_day_title:
                # Replace the default header row with the table's header
                if content:
                    current_day_rows = [content[0]] + content[1:]
                continue

            # Handle time-based activities within day
            if btype == "time_line" and current_day_title:
                parts = re.split(r"\s*[-–]\s*", content, 1)
                if len(parts) == 2:
                    t, a = parts
                    current_day_rows.append([
                        cls._strip_md(t.strip()),
                        cls._strip_md(a.strip())
                    ])
                else:
                    current_day_rows.append(["Flexible", cls._strip_md(content.strip())])
                continue

            # Add paragraphs to day table
            if btype == "paragraph" and current_day_title:
                current_day_rows.append(["", cls._strip_md(content.strip())])
                continue

            # Add bullets to day table
            if btype == "bullets" and current_day_title:
                for item in content:
                    current_day_rows.append(["", cls._strip_md(item)])
                continue

            # Render standalone blocks
            if btype == "title":
                clean_h = cls._strip_md(content)
                story.append(Paragraph(cls._escape(clean_h), h2_style))

            elif btype == "heading":
                clean_h = cls._strip_md(content)
                story.append(Paragraph(cls._escape(clean_h), h2_style))

            elif btype == "subheading":
                clean_h = cls._strip_md(content)
                story.append(Paragraph(cls._escape(clean_h), h3_style))

            elif btype == "paragraph":
                clean_p = cls._strip_md(content)
                # Handle bold text in paragraphs
                if clean_p.startswith("Day ") and "Estimated Cost" in clean_p:
                    story.append(Paragraph(cls._escape(clean_p), bold_body_style))
                elif clean_p.startswith("Travelers:") or clean_p.startswith("Total Estimated") or clean_p.startswith("Planned Budget") or clean_p.startswith("Remaining Budget") or clean_p.startswith("Over Budget"):
                    story.append(Paragraph(cls._escape(clean_p), bold_body_style))
                else:
                    story.append(Paragraph(cls._escape(clean_p).replace("\n", "<br/>"), body_style))

            elif btype == "bullets":
                for item in content:
                    clean_b = cls._strip_md(item)
                    story.append(Paragraph(f"• {cls._escape(clean_b)}", bullet_style))

            elif btype == "table":
                rows = content
                if rows:
                    # Use Paragraph for text wrapping in tables
                    num_cols = len(rows[0]) if rows else 0
                    wrapped_rows = []
                    for i, row in enumerate(rows):
                        if i == 0:
                            wrapped_rows.append([
                                Paragraph(cls._escape(cls._strip_md(c)), cell_bold_style)
                                for c in row
                            ])
                        else:
                            wrapped_rows.append([
                                Paragraph(cls._escape(cls._strip_md(c)), cell_style)
                                for c in row
                            ])

                    # Calculate column widths based on content
                    if num_cols == 5:
                        col_widths = [0.8*inch, 0.7*inch, 2.6*inch, 1.7*inch, 0.7*inch]
                    elif num_cols == 2:
                        col_widths = [1.2*inch, 5.8*inch]
                    else:
                        available = 7.0 * inch
                        col_widths = [available / num_cols] * num_cols

                    tbl = Table(wrapped_rows, colWidths=col_widths, hAlign="LEFT",
                                repeatRows=1)
                    tbl.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), primary),
                        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                        ("FONTSIZE", (0,0), (-1,-1), 8),
                        ("GRID", (0,0), (-1,-1), 0.5, cls.BORDER),
                        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, light_bg]),
                        ("VALIGN", (0,0), (-1,-1), "TOP"),
                        ("TOPPADDING", (0,0), (-1,-1), 5),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                        ("LEFTPADDING", (0,0), (-1,-1), 6),
                    ]))
                    story.append(Spacer(1, 6))
                    story.append(tbl)
                    story.append(Spacer(1, 6))

        # Flush any remaining day table
        flush_day_inline()

        # Footer note
        story.append(Spacer(1, 16))
        footer_style = ParagraphStyle(
            "Footer", parent=styles["Normal"],
            fontSize=7, textColor=cls.MUTED,
            alignment=TA_CENTER,
        )
        story.append(Paragraph(
            f"Generated by AI Smart Flight Agent on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            footer_style
        ))

        # Build PDF
        doc.build(story)
        return output_path

    @classmethod
    def create_comparison_pdf(
        cls,
        itineraries: List[Dict[str, Any]],
        output_path: str,
        user_name: Optional[str] = None
    ) -> str:
        """
        Create comparison PDF for multiple itinerary options.

        Args:
            itineraries: List of itinerary dicts with keys: destination, dates, budget, highlights
            output_path: File path to save PDF
            user_name: Optional user name

        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            rightMargin=0.55*inch, leftMargin=0.55*inch,
            topMargin=0.7*inch, bottomMargin=0.7*inch
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"],
            fontSize=18, textColor=cls.INK,
            alignment=TA_CENTER, spaceAfter=12, fontName="Helvetica-Bold"
        )

        story = []
        story.append(Paragraph("Trip Options Comparison", title_style))
        story.append(Spacer(1, 20))

        # Create comparison table
        headers = ["Option", "Destination", "Dates", "Budget", "Highlights"]
        rows = [headers]

        for idx, itin in enumerate(itineraries, 1):
            rows.append([
                f"Option {idx}",
                itin.get("destination", "N/A"),
                itin.get("dates", "N/A"),
                f"${itin.get('budget', 0):,}",
                itin.get("highlights", "N/A")[:100]
            ])

        table = Table(rows, hAlign="CENTER")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), cls.PUMPKIN_DARK),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("GRID", (0,0), (-1,-1), 0.6, cls.BORDER),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, cls.LIGHT_BG]),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))

        story.append(table)
        doc.build(story)
        return output_path
