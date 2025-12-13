import requests
from config import UNSPLASH_ACCESS_KEY, UNSPLASH_BASE_URL

def search_unsplash_photos(query: str, limit: int = 15):
    """
    Search Unsplash for photos.
    API Docs: https://unsplash.com/documentation#search-photos
    """
    url = f"{UNSPLASH_BASE_URL}/search/photos"
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "per_page": min(limit, 30),  # Unsplash max is 30 per page
        # orientation: omitted to get all orientations (landscape, portrait, squarish)
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # Unsplash returns results in a 'results' array
    return data.get("results", [])
