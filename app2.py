# ai_trip_planner_app.py
# Multi-Agent Trip Planner (CrewAI) with:
# - Modern pumpkin/orange professional UI
# - Full-width output at bottom
# - PDF download option
# - Email PDF to user via SMTP (no itinerary text in email body)
# - Professional PDF formatting (tables + rich layout)
# - In-memory caching for speed
# - Markdown emphasis stripped from PDF output (no ** or *)

from __future__ import annotations

import os
import json
import time
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import concurrent.futures
import requests
import gradio as gr
import faulthandler; faulthandler.enable()

from functools import lru_cache  # ✅ cache

# Email
import smtplib
from email.message import EmailMessage
from pathlib import Path

# CrewAI
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools.tools import SerperDevTool

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


# ===============
# LLM & Tools
# ===============

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

OPENAI_LLM = LLM(
    model="openai/gpt-5",
    # model="openai/gpt-4o",
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0,
)

# Search fallback
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "")
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

serper_tool = SerperDevTool(num_results=3) if SERPER_API_KEY else None
USE_SEARCH = False


def http_get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: int = 8):
    backoff = 0.5
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 2:
                return {"_error": str(e), "_url": url, "_params": params}
            time.sleep(backoff)
            backoff *= 2


def search_tools():
    return [serper_tool] if (USE_SEARCH and serper_tool) else []


# =====================
# Email helper (no itinerary body)
# =====================

def send_pdf_via_email(pdf_path: str, to_email: str, subject: str):
    """
    Sends a PDF via SMTP.
    Email body is ALWAYS short/generic.

    Required env vars:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")

    if not (smtp_host and smtp_user and smtp_pass):
        raise RuntimeError(
            "SMTP not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS."
        )

    if not pdf_path or not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject

    # ✅ fixed short body only
    msg.set_content("Your itinerary is attached in this email.")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=Path(pdf_path).name
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    return True


# =====================
# Professional PDF Generator (inline day tables + strip markdown)
# =====================

class ProfessionalPDFGeneratorV2:
    """
    Converts markdown-like itinerary into a polished PDF:
    - Cover/header + meta
    - Day-by-day tables rendered INLINE (Time / Activity)
    - Bullet sections
    - Markdown tables rendered as PDF tables
    - Strips markdown emphasis (**bold**, *italic*) before rendering.
    """

    PUMPKIN = colors.HexColor("#f78b1f")
    PUMPKIN_DARK = colors.HexColor("#d46d00")
    INK = colors.HexColor("#111827")
    MUTED = colors.HexColor("#6b7280")
    LIGHT_BG = colors.HexColor("#fff7ed")
    BORDER = colors.HexColor("#e5e7eb")

    @staticmethod
    def _escape(text: str) -> str:
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
        return "|" in line and line.strip().startswith("|")

    @staticmethod
    def _parse_md_table(lines: List[str], start_idx: int) -> Tuple[int, List[List[str]]]:
        rows = []
        i = start_idx
        while i < len(lines):
            l = lines[i].strip()
            if not ProfessionalPDFGeneratorV2._is_md_table_line(l):
                break
            cells = [c.strip() for c in l.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                i += 1
                continue
            rows.append(cells)
            i += 1
        return i, rows

    @staticmethod
    def _parse_itinerary(text: str):
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

            if ProfessionalPDFGeneratorV2._is_md_table_line(line):
                flush_paras()
                flush_bullets()
                i2, rows = ProfessionalPDFGeneratorV2._parse_md_table(lines, i)
                if rows:
                    blocks.append(("table", rows))
                i = i2
                continue

            if re.match(r"^(##\s*)?Day\s+\d+[:\-\s].*", line, re.IGNORECASE):
                flush_paras()
                flush_bullets()
                blocks.append(("day_heading", line.replace("##", "").strip()))
                i += 1
                continue

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

            if line.startswith("- ") or line.startswith("* ") or line.startswith("• "):
                flush_paras()
                current_bullets.append(line.lstrip("-*• ").strip())
                i += 1
                continue

            if re.match(r"^\d{1,2}:\d{2}\s*[AaPp][Mm]?\s*[-–]", line):
                flush_paras()
                flush_bullets()
                blocks.append(("time_line", line))
                i += 1
                continue

            current_paras.append(line)
            i += 1

        flush_paras()
        flush_bullets()
        return blocks

    @staticmethod
    def create_itinerary_pdf(itinerary_text: str, destination: str, dates: str,
                             origin: str, budget: int, output_path: str):

        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            rightMargin=0.55*inch, leftMargin=0.55*inch,
            topMargin=0.7*inch, bottomMargin=0.7*inch
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"],
            fontSize=20, textColor=ProfessionalPDFGeneratorV2.INK,
            alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold"
        )

        meta_style = ParagraphStyle(
            "Meta", parent=styles["Normal"],
            fontSize=9, textColor=ProfessionalPDFGeneratorV2.MUTED,
            alignment=TA_CENTER, spaceAfter=10
        )

        h2_style = ParagraphStyle(
            "H2", parent=styles["Heading2"],
            fontSize=12, textColor=ProfessionalPDFGeneratorV2.PUMPKIN_DARK,
            spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold"
        )

        h3_style = ParagraphStyle(
            "H3", parent=styles["Heading3"],
            fontSize=10.5, textColor=ProfessionalPDFGeneratorV2.INK,
            spaceBefore=8, spaceAfter=3, fontName="Helvetica-Bold"
        )

        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=9, leading=12, textColor=ProfessionalPDFGeneratorV2.INK,
            alignment=TA_JUSTIFY, spaceAfter=4
        )

        bullet_style = ParagraphStyle(
            "Bullet", parent=body_style,
            leftIndent=12, bulletIndent=6
        )

        story = []

        # Cover
        story.append(Paragraph(ProfessionalPDFGeneratorV2._escape(destination or "Trip Itinerary"), title_style))
        story.append(Paragraph(
            ProfessionalPDFGeneratorV2._escape(f"{dates}  •  From {origin}  •  Budget ${budget:,}"),
            meta_style
        ))

        meta_table = Table([
            ["Dates", dates],
            ["Origin", origin],
            ["Budget", f"${budget:,} USD"],
            ["Generated", datetime.now().strftime("%B %d, %Y")],
        ], colWidths=[1.3*inch, 5.7*inch])

        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), ProfessionalPDFGeneratorV2.LIGHT_BG),
            ("TEXTCOLOR", (0,0), (-1,-1), ProfessionalPDFGeneratorV2.INK),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.6, ProfessionalPDFGeneratorV2.BORDER),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        blocks = ProfessionalPDFGeneratorV2._parse_itinerary(itinerary_text)

        current_day_title = None
        current_day_rows = []

        def flush_day_inline():
            nonlocal current_day_title, current_day_rows
            if not current_day_title:
                return

            clean_title = ProfessionalPDFGeneratorV2._strip_md(current_day_title)
            story.append(Paragraph(ProfessionalPDFGeneratorV2._escape(clean_title), h3_style))

            day_tbl = Table(current_day_rows, colWidths=[1.2*inch, 5.8*inch], hAlign="LEFT")
            day_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), ProfessionalPDFGeneratorV2.PUMPKIN_DARK),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 9),
                ("GRID", (0,0), (-1,-1), 0.6, ProfessionalPDFGeneratorV2.BORDER),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ProfessionalPDFGeneratorV2.LIGHT_BG]),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(day_tbl)
            story.append(Spacer(1, 8))

            current_day_title = None
            current_day_rows = []

        for btype, content in blocks:

            if current_day_title and btype in ("heading", "subheading", "table", "title"):
                flush_day_inline()

            if btype == "day_heading":
                flush_day_inline()
                current_day_title = content
                current_day_rows = [["Time", "Activity"]]
                continue

            if btype == "time_line" and current_day_title:
                parts = re.split(r"\s*[-–]\s*", content, 1)
                if len(parts) == 2:
                    t, a = parts
                    current_day_rows.append([
                        ProfessionalPDFGeneratorV2._strip_md(t.strip()),
                        ProfessionalPDFGeneratorV2._strip_md(a.strip())
                    ])
                else:
                    current_day_rows.append(["Flexible", ProfessionalPDFGeneratorV2._strip_md(content.strip())])
                continue

            if btype == "paragraph" and current_day_title:
                current_day_rows.append(["Flexible", ProfessionalPDFGeneratorV2._strip_md(content.strip())])
                continue

            if btype == "bullets" and current_day_title:
                for item in content:
                    current_day_rows.append(["Flexible", ProfessionalPDFGeneratorV2._strip_md(item)])
                continue

            if btype == "title":
                clean_h = ProfessionalPDFGeneratorV2._strip_md(content)
                story.append(Paragraph(ProfessionalPDFGeneratorV2._escape(clean_h), h2_style))

            elif btype == "heading":
                clean_h = ProfessionalPDFGeneratorV2._strip_md(content)
                story.append(Paragraph(ProfessionalPDFGeneratorV2._escape(clean_h), h2_style))

            elif btype == "subheading":
                clean_h = ProfessionalPDFGeneratorV2._strip_md(content)
                story.append(Paragraph(ProfessionalPDFGeneratorV2._escape(clean_h), h3_style))

            elif btype == "paragraph":
                clean_p = ProfessionalPDFGeneratorV2._strip_md(content)
                story.append(Paragraph(ProfessionalPDFGeneratorV2._escape(clean_p).replace("\n", "<br/>"), body_style))

            elif btype == "bullets":
                for item in content:
                    clean_b = ProfessionalPDFGeneratorV2._strip_md(item)
                    story.append(Paragraph(f"• {ProfessionalPDFGeneratorV2._escape(clean_b)}", bullet_style))

            elif btype == "table":
                rows = content
                if rows:
                    clean_rows = [
                        [ProfessionalPDFGeneratorV2._strip_md(c) for c in row]
                        for row in rows
                    ]
                    tbl = Table(clean_rows, hAlign="LEFT")
                    tbl.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), ProfessionalPDFGeneratorV2.PUMPKIN),
                        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                        ("FONTSIZE", (0,0), (-1,-1), 9),
                        ("GRID", (0,0), (-1,-1), 0.6, ProfessionalPDFGeneratorV2.BORDER),
                        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ProfessionalPDFGeneratorV2.LIGHT_BG]),
                        ("TOPPADDING", (0,0), (-1,-1), 6),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                    ]))
                    story.append(Spacer(1, 6))
                    story.append(tbl)
                    story.append(Spacer(1, 6))

        flush_day_inline()
        doc.build(story)
        return output_path


# =====================
# Data Fetchers (cached)
# =====================

class DataFetchers:
    """Provider-agnostic helpers with in-memory caching."""

    @staticmethod
    @lru_cache(maxsize=64)
    def _weather_cached(lat_r: float, lon_r: float, start_date: str, end_date: str):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat_r,
            "longitude": lon_r,
            "hourly": "temperature_2m,precipitation,wind_speed_10m",
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "auto",
            "start_date": start_date,
            "end_date": end_date,
        }
        return http_get(url, params=params)

    @staticmethod
    def weather(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
        return DataFetchers._weather_cached(round(lat, 3), round(lon, 3), start_date, end_date)

    @staticmethod
    @lru_cache(maxsize=64)
    def _events_cached(city: str, start: str, end: str):
        key = os.getenv("TICKETMASTER_API_KEY", "")
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {"apikey": key, "city": city, "startDateTime": start, "endDateTime": end, "size": 20}
        return http_get(url, params=params) if key else {"_error": "No Ticketmaster key"}

    @staticmethod
    def events(city: str, start: str, end: str) -> Dict[str, Any]:
        return DataFetchers._events_cached(city.strip().lower(), start, end)

    @staticmethod
    @lru_cache(maxsize=64)
    def _flights_cached(origin: str, dest: str, depart: str, return_date: str):
        return {
            "origin": origin,
            "destination": dest,
            "outbound_date": depart,
            "return_date": return_date,
            "flights": [{"airline": "Example Air", "price_usd": 450, "duration": "3h 30m"}]
        }

    @staticmethod
    def flights(origin: str, dest: str, depart: str, return_date: str) -> Dict[str, Any]:
        return DataFetchers._flights_cached(origin.strip().lower(), dest.strip().lower(), depart, return_date)

    @staticmethod
    @lru_cache(maxsize=64)
    def _hotels_cached(city: str, checkin: str, checkout: str, budget: int):
        return {
            "city": city,
            "checkin": checkin,
            "checkout": checkout,
            "hotels": [{"name": "Example Hotel", "price_per_night": 120, "rating": 4.2}]
        }

    @staticmethod
    def hotels(city: str, checkin: str, checkout: str, budget: int) -> Dict[str, Any]:
        return DataFetchers._hotels_cached(city.strip().lower(), checkin, checkout, int(budget))

    @staticmethod
    @lru_cache(maxsize=64)
    def _traffic_cached(city: str):
        return {"city": city, "traffic_level": "moderate", "best_times": "9am-11am, 2pm-4pm"}

    @staticmethod
    def traffic(city: str) -> Dict[str, Any]:
        return DataFetchers._traffic_cached(city.strip().lower())


# =====================
# Agent & Task Factories
# =====================

class AgentFactory:
    @staticmethod
    def create_city_selector():
        return Agent(
            role="Destination Analyst",
            goal="Select optimal city from options based on preferences",
            backstory="Expert at analyzing destinations and matching to traveler needs",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_weather_agent():
        return Agent(
            role="Weather Specialist",
            goal="Provide accurate weather forecasts",
            backstory="Meteorologist with travel planning expertise",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_events_agent():
        return Agent(
            role="Events Curator",
            goal="Find relevant events and activities",
            backstory="Local events expert and cultural activity specialist",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_health_safety_agent():
        return Agent(
            role="Health & Safety Advisor",
            goal="Ensure traveler safety and health preparedness",
            backstory="Public health and travel safety consultant",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_budget_agent():
        return Agent(
            role="Budget Planner",
            goal="Optimize costs and financial planning",
            backstory="Financial advisor specializing in travel budgets",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_flights_agent():
        return Agent(
            role="Flight Specialist",
            goal="Find best flight options",
            backstory="Aviation industry expert and route optimizer",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_hotels_agent():
        return Agent(
            role="Accommodation Expert",
            goal="Find ideal lodging options",
            backstory="Hospitality industry veteran with global network",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_traffic_agent():
        return Agent(
            role="Transportation Coordinator",
            goal="Plan local transportation and navigation",
            backstory="Urban mobility expert and logistics planner",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_local_expert():
        return Agent(
            role="Local Expert",
            goal="Provide cultural insights and local recommendations",
            backstory="Cultural anthropologist and local guide",
            tools=search_tools(),
            verbose=False,
        )

    @staticmethod
    def create_itinerary_agent():
        return Agent(
            role="Itinerary Synthesizer",
            goal="Create comprehensive day-by-day travel plan",
            backstory="Master trip planner synthesizing all inputs",
            tools=search_tools(),
            verbose=False,
        )


class TaskFactory:
    @staticmethod
    def city_selection_task(agent, cities: str, interests: str):
        return Task(
            description=f"Analyze cities: {cities}. Consider interests: {interests}. Select best destination.",
            expected_output="Selected city name with brief justification",
            agent=agent,
        )

    @staticmethod
    def weather_task(agent, city: str, lat: float, lon: float, start_date: str, end_date: str):
        return Task(
            description=f"Analyze weather for {city} from {start_date} to {end_date}. Provide forecast and recommendations.",
            expected_output="Weather summary with temperature ranges and recommendations",
            agent=agent,
        )

    @staticmethod
    def events_task(agent, city: str, start_iso: str, end_iso: str):
        return Task(
            description=f"Find events in {city} between {start_iso} and {end_iso}",
            expected_output="List of relevant events with details",
            agent=agent,
        )

    @staticmethod
    def health_safety_task(agent, city: str, country: str):
        return Task(
            description=f"Research health and safety for {city}, {country}",
            expected_output="Safety advisories and health recommendations",
            agent=agent,
        )

    @staticmethod
    def flights_task(agent, origin: str, dest: str, start_date: str, end_date: str, prefetched: dict):
        context = f"Prefetched data: {json.dumps(prefetched)}" if prefetched else ""
        return Task(
            description=f"Find flights from {origin} to {dest}. Depart: {start_date}, Return: {end_date}. {context}",
            expected_output="Flight options with prices and recommendations",
            agent=agent,
        )

    @staticmethod
    def hotels_task(agent, city: str, start_date: str, end_date: str, budget_usd: int, prefetched: dict):
        context = f"Prefetched data: {json.dumps(prefetched)}" if prefetched else ""
        return Task(
            description=f"Find hotels in {city} from {start_date} to {end_date}. Budget: ${budget_usd}. {context}",
            expected_output="Hotel recommendations with pricing",
            agent=agent,
        )

    @staticmethod
    def traffic_task(agent, city: str):
        return Task(
            description=f"Analyze transportation options in {city}",
            expected_output="Transportation guide and navigation tips",
            agent=agent,
        )

    @staticmethod
    def budget_task(agent, origin: str, city: str, budget_usd: int):
        return Task(
            description=f"Create budget breakdown for trip from {origin} to {city}. Budget: ${budget_usd}",
            expected_output="Detailed budget allocation",
            agent=agent,
        )

    @staticmethod
    def local_expert_task(agent, city: str, interests: str):
        return Task(
            description=f"Provide local insights for {city}. Interests: {interests}",
            expected_output="Cultural tips, cuisine, customs, hidden gems",
            agent=agent,
        )

    @staticmethod
    def itinerary_task(agent, city: str, start_date: str, end_date: str, constraints: dict, agent_outputs: dict):
        context = f"""
Previous agent findings:
- Weather: {agent_outputs.get('weather', 'N/A')}
- Events: {agent_outputs.get('events', 'N/A')}
- Safety: {agent_outputs.get('safety', 'N/A')}
- Flights: {agent_outputs.get('flights', 'N/A')}
- Hotels: {agent_outputs.get('hotels', 'N/A')}
- Traffic: {agent_outputs.get('traffic', 'N/A')}
- Budget: {agent_outputs.get('budget', 'N/A')}
- Local Tips: {agent_outputs.get('local', 'N/A')}
"""
        return Task(
            description=f"Synthesize all information into day-by-day itinerary for {city} from {start_date} to {end_date}. Constraints: {json.dumps(constraints)}. {context}",
            expected_output="Complete markdown itinerary with daily schedules, incorporating all agent recommendations",
            agent=agent,
        )


# =====================
# Parallel Crew Orchestrator (cached agents)
# =====================

@lru_cache(maxsize=128)
def cached_agent_run(agent_name: str, task_desc: str) -> str:
    factory = AgentFactory()

    if agent_name == "weather":
        agent = factory.create_weather_agent()
    elif agent_name == "events":
        agent = factory.create_events_agent()
    elif agent_name == "safety":
        agent = factory.create_health_safety_agent()
    elif agent_name == "flights":
        agent = factory.create_flights_agent()
    elif agent_name == "hotels":
        agent = factory.create_hotels_agent()
    elif agent_name == "traffic":
        agent = factory.create_traffic_agent()
    elif agent_name == "budget":
        agent = factory.create_budget_agent()
    elif agent_name == "local":
        agent = factory.create_local_expert()
    else:
        agent = factory.create_local_expert()

    task = Task(description=task_desc, expected_output="", agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


class ParallelTripCrew:
    def __init__(
        self,
        origin: str,
        cities: str,
        start_date: str,
        end_date: str,
        interests: str,
        budget_usd: int,
        country: str,
        diet: str,
        risk_tolerance: str,
        run_weather: bool = True,
        run_events: bool = True,
        run_safety: bool = True,
        run_budget: bool = True,
        run_flights: bool = True,
        run_hotels: bool = True,
        run_traffic: bool = True,
    ):
        self.origin = origin
        self.cities = cities
        self.start_date = start_date
        self.end_date = end_date
        self.interests = interests
        self.budget_usd = budget_usd
        self.country = country
        self.diet = diet
        self.risk_tolerance = risk_tolerance

        self.run_weather = run_weather
        self.run_events = run_events
        self.run_safety = run_safety
        self.run_budget = run_budget
        self.run_flights = run_flights
        self.run_hotels = run_hotels
        self.run_traffic = run_traffic

    def run(self):
        factory = AgentFactory()
        tasks = TaskFactory()

        city_selector = factory.create_city_selector()
        select_city_t = tasks.city_selection_task(city_selector, self.cities, self.interests)
        city_crew = Crew(agents=[city_selector], tasks=[select_city_t], process=Process.sequential, verbose=False)
        city_result = city_crew.kickoff()
        selected_city = str(city_result.raw) if hasattr(city_result, 'raw') else str(city_result)
        selected_city = selected_city.split('\n')[0].split('.')[0].strip()

        lat, lon = 40.7128, -74.0060

        pre = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futs = []
            if self.run_weather:
                futs.append(("weather", pool.submit(DataFetchers.weather, lat, lon, self.start_date, self.end_date)))
            if self.run_events:
                futs.append(("events", pool.submit(DataFetchers.events, selected_city, self.start_date, self.end_date)))
            if self.run_flights:
                futs.append(("flights", pool.submit(DataFetchers.flights, self.origin, selected_city, self.start_date, self.end_date)))
            if self.run_hotels:
                futs.append(("hotels", pool.submit(DataFetchers.hotels, selected_city, self.start_date, self.end_date, self.budget_usd)))
            for key, f in futs:
                try:
                    pre[key] = f.result(timeout=12)
                except Exception as _e:
                    pre[key] = {"_error": str(_e)}

        agent_tasks: List[Tuple[str, str]] = []

        if self.run_weather:
            a = factory.create_weather_agent()
            t = tasks.weather_task(a, selected_city, lat, lon, self.start_date, self.end_date)
            agent_tasks.append(("weather", t.description))

        if self.run_events:
            a = factory.create_events_agent()
            t = tasks.events_task(a, selected_city, f"{self.start_date}T00:00:00Z", f"{self.end_date}T23:59:59Z")
            agent_tasks.append(("events", t.description))

        if self.run_safety:
            a = factory.create_health_safety_agent()
            t = tasks.health_safety_task(a, selected_city, self.country)
            agent_tasks.append(("safety", t.description))

        if self.run_flights:
            a = factory.create_flights_agent()
            t = tasks.flights_task(a, self.origin, selected_city, self.start_date, self.end_date, pre.get("flights"))
            agent_tasks.append(("flights", t.description))

        if self.run_hotels:
            a = factory.create_hotels_agent()
            t = tasks.hotels_task(a, selected_city, self.start_date, self.end_date, self.budget_usd, pre.get("hotels"))
            agent_tasks.append(("hotels", t.description))

        if self.run_traffic:
            a = factory.create_traffic_agent()
            t = tasks.traffic_task(a, selected_city)
            agent_tasks.append(("traffic", t.description))

        if self.run_budget:
            a = factory.create_budget_agent()
            t = tasks.budget_task(a, self.origin, selected_city, self.budget_usd)
            agent_tasks.append(("budget", t.description))

        a = factory.create_local_expert()
        t = tasks.local_expert_task(a, selected_city, self.interests)
        agent_tasks.append(("local", t.description))

        agent_outputs = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agent_tasks)) as ex:
            future_to_name = {
                ex.submit(cached_agent_run, name, desc): name
                for name, desc in agent_tasks
            }
            for fut in concurrent.futures.as_completed(future_to_name):
                name = future_to_name[fut]
                try:
                    agent_outputs[name] = fut.result(timeout=180)
                except Exception as e:
                    agent_outputs[name] = f"Error: {str(e)}"

        constraints = {
            "diet": self.diet,
            "risk_tolerance": self.risk_tolerance,
            "origin": self.origin,
            "budget": self.budget_usd,
        }
        itinerary = factory.create_itinerary_agent()
        itinerary_t = tasks.itinerary_task(itinerary, selected_city, self.start_date, self.end_date, constraints, agent_outputs)
        final_crew = Crew(agents=[itinerary], tasks=[itinerary_t], process=Process.sequential, verbose=False)
        result = final_crew.kickoff()
        return result, selected_city


# =====================
# Gradio CSS - Pumpkin Modern Theme
# =====================

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root{
  --page: #ffffff;
  --ink: #1f1f1f;
  --ink-soft: #4a4a4a;
  --muted: #6b7280;
  --pumpkin: #f78b1f;
  --pumpkin-dark: #d46d00;
  --pumpkin-light: #ffb366;
  --pumpkin-soft: #fff4e6;
  --border: #e5e7eb;
  --card: #ffffff;
  --card-alt: #fdf6ed;
  --radius: 14px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
  --shadow-md: 0 8px 24px rgba(0,0,0,0.08);
}

* { font-family: Inter, sans-serif !important; color: var(--ink); }
html, body, .gradio-container { background: var(--page) !important; }
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; padding: 18px !important; }

.header { position: relative; background: var(--card); border: 1px solid var(--border);
  border-radius: calc(var(--radius) + 4px); padding: 18px 20px; box-shadow: var(--shadow-md); overflow: hidden; }
.header::before{ content:""; position:absolute; inset:0 0 auto 0; height:6px;
  background: linear-gradient(90deg, var(--pumpkin), var(--pumpkin-light), var(--pumpkin-dark)); }
.header h1{ font-size: 22px !important; font-weight: 800 !important; margin: 6px 0 4px 0 !important; }
.header p{ margin: 0 !important; font-size: 13px !important; color: var(--muted) !important; }

.card { background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px; box-shadow: var(--shadow-sm); }
.card-title{ font-size: 13px !important; font-weight: 800 !important; color: var(--pumpkin-dark) !important;
  margin-bottom: 8px !important; letter-spacing: 0.3px; text-transform: uppercase; }

label, .label, .gr-input-label{ font-size: 12px !important; font-weight: 700 !important; color: var(--ink-soft) !important; margin-bottom: 6px !important; }

input[type="text"], textarea, select{
  background: var(--card-alt) !important; border: 1.5px solid var(--border) !important; border-radius: 10px !important;
  padding: 10px 11px !important; font-size: 13px !important; transition: 150ms ease; }
input:focus, textarea:focus, select:focus{ border-color: var(--pumpkin) !important; box-shadow: 0 0 0 3px rgba(247,139,31,0.25) !important; outline: none !important; }

button, .gr-button{
  background: linear-gradient(135deg, var(--pumpkin-dark), var(--pumpkin)) !important; color: white !important; border: none !important;
  padding: 12px 16px !important; font-size: 14px !important; font-weight: 800 !important; border-radius: 12px !important;
  box-shadow: 0 8px 20px rgba(247,139,31,0.25) !important; transition: 150ms ease-in-out; }
button:hover, .gr-button:hover{ transform: translateY(-2px) !important; box-shadow: 0 10px 25px rgba(247,139,31,0.32) !important; }

.checkbox-group label, .radio-group label{
  background: var(--pumpkin-soft) !important; border: 1px solid var(--pumpkin-light) !important; color: var(--ink) !important;
  padding: 6px 10px !important; border-radius: 999px !important; font-size: 12px !important; font-weight: 600 !important; }
.checkbox-group label:hover, .radio-group label:hover{ background: var(--pumpkin-light) !important; color: white !important; }

.output{
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px !important; min-height: 450px !important; max-height: 720px !important; overflow: auto;
  font-size: 14px !important; line-height: 1.65; box-shadow: var(--shadow-sm);
}

.output h1, .output h2, .output h3{ color: var(--pumpkin-dark) !important; font-weight: 800 !important; }
.output ul{ margin-left: 20px; }
.gr-row{ gap: 12px !important; } .gr-column{ gap: 12px !important; }

footer, .footer, .gradio-container footer{
  display:none !important; visibility:hidden !important; height:0 !important; margin:0 !important; padding:0 !important;
}
"""


# =====================
# Run Trip + PDF
# =====================

def run_trip(origin, cities, date_range, interests, budget, country,
             diet, risk, toggles, mode):
    yield "🔄 AI agents are working....Please wait for a while.", None, "Starting...", "Trip"

    global USE_SEARCH
    USE_SEARCH = (mode == "Deep Search") and bool(SERPER_API_KEY)

    try:
        start_date, end_date = [s.strip() for s in date_range.split("to")]
    except:
        yield "❌ Date format must be: YYYY-MM-DD to YYYY-MM-DD", None, "", "Trip"
        return

    budget_usd = int(float(budget)) if str(budget).strip() else 1500

    crew = ParallelTripCrew(
        origin=origin.strip(),
        cities=cities.strip(),
        start_date=start_date,
        end_date=end_date,
        interests=interests.strip(),
        budget_usd=budget_usd,
        country=country.strip() or "USA",
        diet=diet.strip(),
        risk_tolerance=risk or "medium",
        run_weather="Weather" in (toggles or []),
        run_events="Events" in (toggles or []),
        run_safety="Safety" in (toggles or []),
        run_budget="Budget" in (toggles or []),
        run_flights="Flights" in (toggles or []),
        run_hotels="Hotels" in (toggles or []),
        run_traffic="Traffic" in (toggles or []),
    )

    try:
        res, selected_city = crew.run()
        itinerary_text = res.raw if hasattr(res, "raw") else str(res)

        yield itinerary_text, None, "✅ Itinerary ready. Generating PDF...", selected_city

        clean_city = selected_city.replace(" ", "_").replace("/", "_")[:15]
        pdf_filename = f"Trip_{clean_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = f"/tmp/{pdf_filename}"

        ProfessionalPDFGeneratorV2.create_itinerary_pdf(
            itinerary_text,
            selected_city,
            f"{start_date} to {end_date}",
            origin,
            budget_usd,
            pdf_path
        )

        yield itinerary_text, pdf_path, "📄 PDF ready. Download or email it below.", selected_city

    except Exception as e:
        import traceback
        yield f"❌ Error: {str(e)}\n\n{traceback.format_exc()}", None, "", "Trip"


def email_pdf(pdf_file, to_email, city_name):
    if not pdf_file:
        return "❌ No PDF available yet. Generate itinerary first."
    if not to_email or "@" not in to_email:
        return "❌ Please enter a valid email address."

    pdf_path = pdf_file if isinstance(pdf_file, str) else pdf_file.name

    try:
        send_pdf_via_email(
            pdf_path=pdf_path,
            to_email=to_email.strip(),
            subject=f"Your Trip Itinerary: {city_name}"
        )
        return f"✅ Sent to {to_email}"
    except Exception as e:
        return f"❌ Email failed: {str(e)}"


# =====================
# Gradio UI
# =====================

with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
    gr.HTML("""
    <div class="header">
        <h1>🌍 AI Trip Planner</h1>
        <p>Multi-agent itinerary planning system</p>
    </div>
    """)

    with gr.Group(elem_classes="card"):
        gr.Markdown("Trip Details", elem_classes="card-title")

        with gr.Row():
            origin = gr.Textbox(label="From", placeholder="Seattle, Chicago etc.")
            cities = gr.Textbox(label="Destinations", placeholder="Orlando, Miami etc.")

        date_range = gr.Textbox(label="Dates", placeholder="2025-12-15 to 2025-12-22")
        interests = gr.Textbox(label="Interests", placeholder="Food, History, Museums etc.")

        with gr.Row():
            budget = gr.Textbox(label="Budget (USD)", value="2000")
            country = gr.Textbox(label="Country", value="USA")

        with gr.Row():
            diet = gr.Textbox(label="Dietary", placeholder="Halal, Vegan etc.")
            risk = gr.Dropdown(["low", "medium", "high"], value="medium", label="Risk Level")

    with gr.Group(elem_classes="card"):
        gr.Markdown("Agents & Search Mode", elem_classes="card-title")

        agent_toggles = gr.CheckboxGroup(
            ["Weather", "Events", "Safety", "Budget", "Flights", "Hotels", "Traffic"],
            value=["Weather", "Events", "Safety", "Budget", "Flights", "Hotels", "Traffic"],
            label="Enable Agents"
        )

        mode = gr.Radio(["Fast Search", "Deep Search"], value="Fast Search", label="Mode")
        plan_btn = gr.Button("🚀 Plan My Trip")

    output_text = gr.Markdown("*Your itinerary will appear below...*", elem_classes="output")

    with gr.Group(elem_classes="card"):
        gr.Markdown("PDF Options", elem_classes="card-title")

        pdf_file = gr.File(label="Download Itinerary PDF", interactive=False)

        selected_city_state = gr.State("Trip")

        with gr.Row():
            email_to = gr.Textbox(label="Send PDF to Email", placeholder="you@example.com", scale=3)
            send_btn = gr.Button("📧 Send PDF", scale=1)

        email_status = gr.Markdown("")

    plan_btn.click(
        run_trip,
        inputs=[origin, cities, date_range, interests, budget, country, diet, risk, agent_toggles, mode],
        outputs=[output_text, pdf_file, email_status, selected_city_state]
    )

    send_btn.click(
        email_pdf,
        inputs=[pdf_file, email_to, selected_city_state],
        outputs=[email_status]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7865,
        share=True,
        #share=False,
        show_error=True
    )

