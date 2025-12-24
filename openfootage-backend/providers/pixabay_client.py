# providers/pixabay_client.py

from typing import List
import os
import requests

# 1) Try to get the key from config *if you have it*
try:
    from config import PIXABAY_API_KEY as CONFIG_PIXABAY_KEY  # type: ignore
except Exception:
    CONFIG_PIXABAY_KEY = None

# 2) Fallback to environment variable
ENV_PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY")

# 3) Final value: config wins, then env, else empty
PIXABAY_API_KEY = CONFIG_PIXABAY_KEY or ENV_PIXABAY_KEY

PIXABAY_PHOTO_API_BASE = "https://pixabay.com/api"
PIXABAY_VIDEO_API_BASE = "https://pixabay.com/api/videos"


def _ensure_api_key():
    if not PIXABAY_API_KEY:
        # This will show up in your Uvicorn logs if key is missing
        raise RuntimeError("PIXABAY_API_KEY is not set (config or environment)")


def search_pixabay_videos(query: str, limit: int = 40) -> List[dict]:
    """
    Search Pixabay VIDEOS (https://pixabay.com/api/videos/).
    Returns the 'hits' list from the Pixabay JSON.
    """
    _ensure_api_key()

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": limit,
        "video_type": "all",
        "safesearch": "true",
    }

    response = requests.get(
        PIXABAY_VIDEO_API_BASE,
        params=params,
        timeout=4,
    )

    # DEBUG
    print(f"[DEBUG] Pixabay VIDEO request URL: {response.url} (status={response.status_code})")

    response.raise_for_status()
    data = response.json()

    print(f"[DEBUG] Pixabay VIDEO totalHits for '{query}': {data.get('totalHits')}")
    return data.get("hits", [])


def search_pixabay_photos(query: str, limit: int = 40) -> List[dict]:
    """
    Search Pixabay PHOTOS (https://pixabay.com/api/).
    Returns the 'hits' list from the Pixabay JSON.
    """
    _ensure_api_key()

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": limit,          # 3–200 allowed
        "image_type": "photo",      # as per docs
        "safesearch": "true",       # keep it clean
        "orientation": "all",
    }

    response = requests.get(
        PIXABAY_PHOTO_API_BASE,
        params=params,
        timeout=4,
    )

    # DEBUG
    print(f"[DEBUG] Pixabay PHOTO request URL: {response.url} (status={response.status_code})")

    response.raise_for_status()
    data = response.json()

    print(f"[DEBUG] Pixabay PHOTO totalHits for '{query}': {data.get('totalHits')}")
    return data.get("hits", [])


def search_pixabay_vectors(query: str, limit: int = 40) -> List[dict]:
    """
    Search Pixabay VECTORS (https://pixabay.com/api/).
    Same as photos but with image_type=vector.
    Returns the 'hits' list from the Pixabay JSON.
    """
    _ensure_api_key()

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": limit,
        "image_type": "vector",    # vectors!
        "safesearch": "true",
        "orientation": "all",
    }

    response = requests.get(
        PIXABAY_PHOTO_API_BASE,
        params=params,
        timeout=4,
    )

    print(f"[DEBUG] Pixabay VECTOR request URL: {response.url} (status={response.status_code})")

    response.raise_for_status()
    data = response.json()

    print(f"[DEBUG] Pixabay VECTOR totalHits for '{query}': {data.get('totalHits')}")
    return data.get("hits", [])
