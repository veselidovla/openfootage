# providers/coverr_client.py

from typing import List
import os
import requests

# Try to get the key from config (if you add it there)
try:
    from config import COVERR_API_KEY as CONFIG_COVERR_KEY  # type: ignore
except Exception:
    CONFIG_COVERR_KEY = None

# Fallback to environment variable
ENV_COVERR_KEY = os.environ.get("57d3d21dce2b089260e0c44610823dba")

# Final value: config wins, then env, else empty
COVERR_API_KEY = CONFIG_COVERR_KEY or ENV_COVERR_KEY

COVERR_API_BASE = "https://api.coverr.co/videos"


def _ensure_api_key():
    if not COVERR_API_KEY:
        raise RuntimeError(
            "COVERR_API_KEY is not set (add COVERR_API_KEY to config.py or environment)"
        )


def search_coverr_videos(query: str, limit: int = 40) -> List[dict]:
    """
    Search Coverr VIDEOS.

    Uses:
      GET https://api.coverr.co/videos?query=...&page_size=...

    Docs: https://api.coverr.co/docs/videos/
    """
    _ensure_api_key()

    # Coverr uses page & page_size; we keep it simple and just use page=0
    params = {
        "query": query,
        "page": 0,
        "page_size": limit,
        "urls": True,  # include urls in the response
        "api_key": COVERR_API_KEY,  # auth via query param
    }

    response = requests.get(
        COVERR_API_BASE,
        params=params,
        timeout=10,
    )

    # Debug logging so we can see what's happening if something goes wrong
    print(
        f"[DEBUG] Coverr VIDEO request URL: {response.url} "
        f"(status={response.status_code})"
    )

    response.raise_for_status()
    data = response.json()

    hits = data.get("hits", []) or []
    print(
        f"[DEBUG] Coverr VIDEO total for '{query}': "
        f"{data.get('total')} (hits returned: {len(hits)})"
    )

def search_coverr_videos(query: str, limit: int = 20) -> list[dict]:
    """Search Coverr videos with better error handling"""
    try:
        params = {
            "query": query,
            "page": 0,
            "page_size": min(limit, 80),
            "urls": True,
        }
        if COVERR_API_KEY:
            params["api_key"] = COVERR_API_KEY

        response = requests.get(
            "https://api.coverr.co/videos",
            params=params,
            timeout=4,
        )
        response.raise_for_status()
        data = response.json()
        
        # ADD NULL CHECK HERE
        hits = data.get("hits") or []
        if not isinstance(hits, list):
            return []
            
        print(f"[DEBUG] Coverr VIDEO total for '{query}': {data.get('total', 0)} (hits returned: {len(hits)})")
        return hits
        
    except Exception as e:
        print(f"[ERROR] Coverr search failed: {e}")
        return []
