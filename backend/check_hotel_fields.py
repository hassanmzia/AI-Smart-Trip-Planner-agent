#!/usr/bin/env python3
"""Check raw hotel data structure from SerpAPI"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_agent.settings')
sys.path.insert(0, '/home/user/ai-smart-flight-agent/backend')
django.setup()

from django.conf import settings
import requests
import json

# SerpAPI hotel search
params = {
    "engine": "google_hotels",
    "q": "New York JFK Airport",
    "check_in_date": "2026-02-20",
    "check_out_date": "2026-02-27",
    "adults": 2,
    "currency": "USD",
    "gl": "us",
    "hl": "en",
    "api_key": settings.SERP_API_KEY
}

print("🔍 Fetching raw hotel data from SerpAPI...\n")
response = requests.get("https://serpapi.com/search", params=params, timeout=30)
data = response.json()

if 'properties' in data and data['properties']:
    hotel = data['properties'][0]
    print(f"First hotel: {hotel.get('name', 'Unknown')}\n")

    # Check images structure
    print("📸 Images field:")
    images = hotel.get('images', [])
    print(f"Type: {type(images)}")
    if images:
        print(f"First image type: {type(images[0])}")
        print(f"First image: {images[0]}")
        print(f"Total images: {len(images)}\n")
    else:
        print("No images found\n")

    # Check link structure
    print("🔗 Link field:")
    link = hotel.get('link')
    print(f"Type: {type(link)}")
    print(f"Value: {link}\n")

    # Show all top-level fields
    print("📋 All hotel fields:")
    for key in sorted(hotel.keys()):
        value = hotel[key]
        if isinstance(value, (list, dict)):
            print(f"  {key}: {type(value).__name__} (length: {len(value) if isinstance(value, (list, dict)) else 'N/A'})")
        else:
            print(f"  {key}: {value}")
else:
    print("❌ No hotels found in response")
    print(f"Response keys: {data.keys()}")
