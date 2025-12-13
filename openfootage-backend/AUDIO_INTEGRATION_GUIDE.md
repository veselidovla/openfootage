# Adding Audio Support (Music & SFX)

## Current Status

❌ **Pixabay does NOT provide an audio API**

Their API only supports:
- ✅ Images (photos, illustrations, vectors)
- ✅ Videos

## Alternative Audio Providers

To add music and SFX support, you'll need to integrate one of these providers:

---

### 1. Freesound (Recommended for SFX)

**Website:** https://freesound.org/  
**API Docs:** https://freesound.org/docs/api/  
**Type:** Free sound effects library  
**Auth:** API key (free registration)

**Pros:**
- Huge library of sound effects
- Creative Commons licensed
- Well-documented API
- Search by tags, categories, duration

**API Example:**
```bash
GET https://freesound.org/apiv2/search/text/?query=explosion&token=YOUR_API_KEY
```

**Response includes:**
- `id`, `name`, `description`
- `previews` (mp3, ogg URLs)
- `download` (original file URL)
- `duration`, `filesize`
- `tags`, `license`

---

### 2. Mixkit (Recommended for Music)

**Website:** https://mixkit.co/  
**Free Music:** https://mixkit.co/free-stock-music/  
**Free SFX:** https://mixkit.co/free-sound-effects/  
**API:** Not officially documented, may need web scraping

**Pros:**
- High-quality music tracks
- Royalty-free, no attribution required
- Categories: cinematic, corporate, beats, etc.

**Cons:**
- No official API (would need to scrape or contact them)

---

### 3. YouTube Audio Library

**Website:** https://www.youtube.com/audiolibrary  
**Type:** Royalty-free music

**Pros:**
- High-quality music
- Free for commercial use
- Filter by mood, genre, instrument

**Cons:**
- No official API
- Would require web scraping

---

## Implementation Guide (Freesound Example)

### Step 1: Create Freesound Client

Create `providers/freesound_client.py`:

```python
import requests
from typing import List
from config import FREESOUND_API_KEY

FREESOUND_BASE_URL = "https://freesound.org/apiv2"

def search_freesound_sfx(query: str, limit: int = 25) -> List[dict]:
    """
    Search Freesound for sound effects.
    """
    url = f"{FREESOUND_BASE_URL}/search/text/"
    
    params = {
        "query": query,
        "token": FREESOUND_API_KEY,
        "page_size": limit,
        "fields": "id,name,description,previews,duration,tags,license,url",
    }
    
    response = requests.get(url, params=params, timeout=4)
    response.raise_for_status()
    
    data = response.json()
    return data.get("results", [])
```

### Step 2: Create Normalizer

Create `normalizers/freesound_normalizer.py`:

```python
def normalize_freesound_sfx(raw: dict) -> dict:
    """
    Normalize Freesound data to OpenFootage schema.
    """
    sfx_id = raw.get("id")
    name = raw.get("name") or "Untitled SFX"
    description = raw.get("description") or ""
    page_url = raw.get("url") or ""
    duration = raw.get("duration") or 0
    tags = raw.get("tags") or []
    
    # Freesound provides preview URLs
    previews = raw.get("previews") or {}
    audio_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3") or ""
    
    # Use waveform image as preview if available
    images = raw.get("images") or {}
    preview_image = images.get("waveform_m") or images.get("spectral_m") or ""
    
    return {
        "id": f"freesound-{sfx_id}",
        "provider": "freesound",
        "type": "sfx",
        
        "title": name,
        "description": description,
        "page_url": page_url,
        "preview_image_url": preview_image,
        "audio_url": audio_url,
        
        "duration": duration,
        "duration_seconds": duration,
        "tags": ", ".join(tags) if isinstance(tags, list) else tags,
        
        "license": raw.get("license") or "",
        
        # Not applicable
        "width": None,
        "height": None,
        "video_url": None,
    }
```

### Step 3: Wire into main.py

Update `main.py`:

```python
# Add imports
from providers.freesound_client import search_freesound_sfx
from normalizers.freesound_normalizer import normalize_freesound_sfx

# In fetch_and_index_all, replace the SFX section:
if fetch_sfx:
    try:
        raw = search_freesound_sfx(query=query, limit=limit)
        for r in raw:
            doc = normalize_freesound_sfx(r)
            doc["provider"] = "freesound"
            doc["type"] = "sfx"
            docs.append(doc)
    except Exception as e:
        logger.error(f"Freesound SFX error: {e}")
```

### Step 4: Add API Key to config.py

```python
FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY", "your_key_here")
```

### Step 5: Test

```bash
curl "http://localhost:8000/search/simple?query=explosion&type=sfx"
```

---

## Quick Integration Checklist

For any audio provider:

1. ✅ Sign up and get API key
2. ✅ Create provider client (`providers/{provider}_client.py`)
3. ✅ Create normalizer (`normalizers/{provider}_normalizer.py`)
4. ✅ Add imports to `main.py`
5. ✅ Wire into `fetch_and_index_all` function
6. ✅ Add API key to `config.py` and `.env`
7. ✅ Test the endpoint

---

## Recommended Setup

For a complete audio solution:

- **SFX:** Freesound (free, well-documented API)
- **Music:** Mixkit (if they provide API access) or YouTube Audio Library (with scraping)

Or use both Freesound for everything (they have music too, but less curated).

---

## Current Backend State

✅ **Ready for integration:**
- Audio normalizer schema defined
- Main search logic supports `music` and `sfx` types
- Logging in place for debugging
- Frontend guide includes audio card layouts

🔧 **What's needed:**
- Choose audio provider(s)
- Implement provider client
- Wire into search pipeline
- Add API keys to config

**Time estimate:** 1-2 hours per provider

---

Last updated: December 8, 2025
