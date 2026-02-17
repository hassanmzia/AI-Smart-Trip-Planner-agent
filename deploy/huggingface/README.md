---
title: AI Smart Trip Planner
emoji: ✈️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# AI Smart Trip Planner

Multi-agent AI-powered travel planning platform built with Django, React, LangChain, and LangGraph.

## Features

- **AI-Powered Trip Planning** - Multi-agent system with 10+ specialized agents
- **Flight & Hotel Search** - Real-time search via SerpAPI
- **Smart Itineraries** - AI-generated day-by-day travel plans
- **Restaurant & Attraction Recommendations**
- **Weather Forecasts & Safety Information**
- **Payments** - Stripe integration for booking

## Setup (Hugging Face Spaces)

1. Create a new Space with **Docker** SDK
2. Copy this directory's contents to your Space repo
3. Set the following **Secrets** in Space Settings:
   - `OPENAI_API_KEY` (required for AI agents)
   - `SERP_API_KEY` (required for travel search)
   - `STRIPE_SECRET_KEY` (optional, for payments)
   - `STRIPE_PUBLISHABLE_KEY` (optional, for payments)
   - `WEATHER_API_KEY` (optional, for weather)

4. The Space will auto-build and deploy

## Default Login

- **Email**: admin@trip-planner.com
- **Password**: admin123

> Change the default password after first login!

## Architecture

This Space runs as a single container with:
- **Nginx** (port 7860) - Reverse proxy serving frontend + routing to backend
- **Django** (port 8109) - Backend REST API with LangChain agents
- **MCP Server** (port 8107) - FastAPI agent communication server
- **SQLite** - Persistent database (stored in `/data`)

## Limitations on HF Spaces

- No Redis (uses in-memory cache and channel layer)
- No RabbitMQ/Celery (async tasks run synchronously)
- SQLite instead of PostgreSQL (sufficient for demo/small scale)
- WebSocket functionality is limited
