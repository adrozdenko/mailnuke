"""Preset filter endpoints."""

import sys
import os
from fastapi import APIRouter

# Add engine to path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))

from constants import DEFAULT_FILTERS, FILTER_PRESETS

router = APIRouter()


@router.get("/presets")
async def list_presets():
    """Return all available filter presets."""
    presets = []

    presets.append({
        "id": "default",
        "name": "Default",
        "description": "6 months old, preserve attachments",
        "filters": DEFAULT_FILTERS,
    })

    descriptions = {
        "newsletters": "Newsletter cleanup — 30 days, marketing keywords",
        "github_notifications": "GitHub notifications — 7 days old",
        "large_emails": "Large emails — 90 days, 10MB+ size",
        "social_media": "Social media — 14 days, FB/Twitter/LinkedIn",
        "promotional": "Promotional — 60 days, sale keywords",
    }

    for key, filters in FILTER_PRESETS.items():
        presets.append({
            "id": key,
            "name": key.replace("_", " ").title(),
            "description": descriptions.get(key, ""),
            "filters": filters,
        })

    return {"presets": presets}
