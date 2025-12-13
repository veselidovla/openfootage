# providers/pexels_client.py

import requests
from config import PEXELS_API_KEY, PEXELS_BASE_URL


def search_pexels_videos(query: str, limit: int = 10, page: int = 1) -> list[dict]:
    """
    Call the Pexels VIDEO API and return a list of raw video dicts.
    """
    url = f"{PEXELS_BASE_URL}/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": limit,
        "page": page,
    }

    response = requests.get(url, headers=headers, params=params, timeout=4)
    response.raise_for_status()

    data = response.json() or {}
    videos = data.get("videos") or []
    return videos

from typing import List  # you probably already have this at the top
import requests          # and this too
from config import PEXELS_API_KEY  # already used for videos


def search_pexels_photos(query: str, limit: int = 40) -> List[dict]:
    """
    Search Pexels PHOTOS API.

    Returns a list of raw photo dicts from Pexels.
    """
    url = "https://api.pexels.com/v1/search"
    per_page = min(limit, 80)
    headers = {
        "Authorization": PEXELS_API_KEY,
    }
    params = {
        "query": query,
        "per_page": per_page,
        "page": 1,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=4)
    resp.raise_for_status()
    data = resp.json()
    return data.get("photos", [])
