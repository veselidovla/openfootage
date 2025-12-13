# providers/freesound_client.py

from typing import List
import os
import requests

# Try to get the key from config
try:
    from config import FREESOUND_API_KEY as CONFIG_FREESOUND_KEY  # type: ignore
except Exception:
    CONFIG_FREESOUND_KEY = None

# Fallback to environment variable
ENV_FREESOUND_KEY = os.environ.get("FREESOUND_API_KEY")

# Final value: config wins, then env, else empty
FREESOUND_API_KEY = CONFIG_FREESOUND_KEY or ENV_FREESOUND_KEY

FREESOUND_API_BASE = "https://freesound.org/apiv2"


def _ensure_api_key():
    if not FREESOUND_API_KEY:
        raise RuntimeError(
            "FREESOUND_API_KEY is not set (add to config.py or environment)"
        )


def search_freesound_sfx(query: str, limit: int = 25) -> List[dict]:
    """
    Search Freesound for sound effects.
    
    API Docs: https://freesound.org/docs/api/
    Optimization: Request all fields in initial search to avoid detail fetches.
    """
    _ensure_api_key()

    params = {
        "query": query,
        "token": FREESOUND_API_KEY,
        "page_size": min(limit, 150),  # Max 150 per page
        "format": "json",
        # Request all needed fields upfront to avoid detail fetches
        "fields": "id,name,tags,description,duration,previews,images,license,url,avg_rating,num_downloads,num_ratings,created",
    }

    try:
        # First: Search to get IDs
        response = requests.get(
            f"{FREESOUND_API_BASE}/search/text/",
            params=params,
            timeout=10,  # Increased for reliability
        )

        print(f"[DEBUG] Freesound SFX search (status={response.status_code})")

        if response.status_code != 200:
            print(f"[ERROR] Freesound API error: {response.status_code}")
            return []

        data = response.json()
        results = data.get("results", [])
        total_count = data.get("count", 0)
        print(f"[DEBUG] Freesound SFX totalHits for '{query}': {total_count} (returned: {len(results)})")
        
        # Return results directly - all fields already included via 'fields' parameter
        return results[:min(limit, len(results))]
    
    except Exception as e:
        print(f"[ERROR] Freesound SFX search failed: {e}")
        return []


def search_freesound_music(query: str, limit: int = 25) -> List[dict]:
    """
    Search Freesound for music tracks.
    
    Optimization: Use better query terms and request all fields upfront.
    """
    _ensure_api_key()

    # Improved query: add musical context terms
    # If query is already specific, use it; otherwise enhance it
    if len(query.split()) > 2 or any(term in query.lower() for term in ['loop', 'beat', 'track', 'instrumental', 'melody']):
        music_query = query
    else:
        music_query = f"{query} music loop"

    params = {
        "query": music_query,
        "token": FREESOUND_API_KEY,
        "page_size": min(limit, 150),
        "format": "json",
        # Request all needed fields upfront
        "fields": "id,name,tags,description,duration,previews,images,license,url,avg_rating,num_downloads,num_ratings,created",
    }

    try:
        # First: Search to get IDs
        response = requests.get(
            f"{FREESOUND_API_BASE}/search/text/",
            params=params,
            timeout=10,  # Increased for reliability
        )

        print(f"[DEBUG] Freesound MUSIC search (status={response.status_code})")

        if response.status_code != 200:
            print(f"[ERROR] Freesound API error: {response.status_code}")
            return []

        data = response.json()
        results = data.get("results", [])
        total_count = data.get("count", 0)
        print(f"[DEBUG] Freesound MUSIC totalHits for '{music_query}': {total_count} (returned: {len(results)})")
        
        # Return results directly - all fields already included via 'fields' parameter
        return results[:min(limit, len(results))]
    
    except Exception as e:
        print(f"[ERROR] Freesound music search failed: {e}")
        return []
