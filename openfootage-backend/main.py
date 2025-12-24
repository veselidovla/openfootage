# main.py - CLEAN, WORKING, FILTER-READY VERSION

from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from math import sqrt
from datetime import datetime
import logging
import re

from meilisearch import Client
from openai import OpenAI

from config import (
    MEILISEARCH_URL,
    MEILISEARCH_API_KEY,
    OPENAI_API_KEY,
    OPENAI_EMBEDDINGS_MODEL,
)

# Provider search + normalizers
from providers.pexels_client import search_pexels_videos, search_pexels_photos
from normalizers.pexels_normalizer import normalize_pexels_video
from normalizers.pexels_photo_normalizer import normalize_pexels_photo

from providers.pixabay_client import search_pixabay_videos, search_pixabay_photos, search_pixabay_vectors
from normalizers.pixabay_normalizer import normalize_pixabay_video
from normalizers.pixabay_photo_normalizer import normalize_pixabay_photo, normalize_pixabay_vector

from providers.freesound_client import search_freesound_sfx, search_freesound_music
from normalizers.freesound_normalizer import normalize_freesound_sfx, normalize_freesound_music

from providers.unsplash_client import search_unsplash_photos
from normalizers.unsplash_normalizer import normalize_unsplash_photo


# -----------------------------------
# FastAPI SETUP
# -----------------------------------

INDEX_NAME = "videos"
app = FastAPI(title="OpenFootage API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

meili_client = Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------------
# Filter Options Metadata
# -----------------------------------

@app.get("/filters")
def get_filters(asset_type: Optional[str] = Query(None, alias="type")):
    """
    Get available filter options organized by priority:
    1. Primary filters (mode, provider, asset type) - always visible
    2. Asset-specific filters - shown based on selected asset type
    
    Provider options are filtered based on asset type:
    - video: Pexels, Pixabay
    - photo: Pexels, Pixabay, Unsplash
    - vector: Pixabay
    - music/sfx: Freesound
    """
    # Determine available providers based on asset type
    provider_options = [{"value": "all", "label": "All Providers"}]
    
    if not asset_type or asset_type == "all":
        # Show all providers when no type selected
        provider_options.extend([
            {"value": "pexels", "label": "Pexels"},
            {"value": "pixabay", "label": "Pixabay"},
            {"value": "unsplash", "label": "Unsplash"},
            {"value": "freesound", "label": "Freesound"}
        ])
    elif asset_type == "video":
        provider_options.extend([
            {"value": "pexels", "label": "Pexels"},
            {"value": "pixabay", "label": "Pixabay"}
        ])
    elif asset_type == "photo":
        provider_options.extend([
            {"value": "pexels", "label": "Pexels"},
            {"value": "pixabay", "label": "Pixabay"},
            {"value": "unsplash", "label": "Unsplash"}
        ])
    elif asset_type == "vector":
        provider_options.extend([
            {"value": "pixabay", "label": "Pixabay"}
        ])
    elif asset_type == "illustration":
        provider_options.extend([
            {"value": "unsplash", "label": "Unsplash"}
        ])
    elif asset_type in ("music", "sfx"):
        provider_options.extend([
            {"value": "freesound", "label": "Freesound"}
        ])
    
    response = {
        "primary": {
            "mode": {
                "label": "Search Mode",
                "options": [
                    {"value": "simple", "label": "Simple"},
                    {"value": "smart", "label": "Smart"},
                    {"value": "semantic", "label": "Semantic"},
                    {"value": "hybrid", "label": "Hybrid"}
                ]
            },
            "provider": {
                "label": "Provider",
                "options": provider_options
            },
            "type": {
                "label": "Asset Type",
                "options": [
                    {"value": "video", "label": "Videos"},
                    {"value": "photo", "label": "Photos"},
                    {"value": "vector", "label": "Vectors"},
                    {"value": "illustration", "label": "Illustrations"},
                    {"value": "music", "label": "Music"},
                    {"value": "sfx", "label": "Sound Effects"}
                ]
            }
        },
        "assetFilters": {
            "video": {
                "aspect_ratio": {
                    "label": "Aspect Ratio",
                    "options": [
                        {"value": "16:9", "label": "16:9 (Landscape)"},
                        {"value": "9:16", "label": "9:16 (Portrait)"},
                        {"value": "1:1", "label": "1:1 (Square)"},
                        {"value": "4:3", "label": "4:3 (Standard)"},
                        {"value": "other", "label": "Other"}
                    ]
                },
                "resolution": {
                    "label": "Resolution",
                    "options": [
                        {"value": "UHD", "label": "UHD (2160p+)"},
                        {"value": "4K", "label": "4K (1440p+)"},
                        {"value": "Full HD", "label": "Full HD (1080p)"},
                        {"value": "HD", "label": "HD (720p)"},
                        {"value": "SD", "label": "SD (<720p)"}
                    ]
                },
                "duration": {
                    "label": "Duration",
                    "options": [
                        {"value": "short", "label": "Short (<30s)"},
                        {"value": "medium", "label": "Medium (30s-2min)"},
                        {"value": "long", "label": "Long (>2min)"}
                    ]
                }
            },
            "photo": {
                "orientation": {
                    "label": "Orientation",
                    "options": [
                        {"value": "horizontal", "label": "Landscape"},
                        {"value": "vertical", "label": "Portrait"},
                        {"value": "square", "label": "Square"}
                    ]
                },
                "size": {
                    "label": "Resolution",
                    "options": [
                        {"value": "web", "label": "Web (<5MP)"},
                        {"value": "standard", "label": "Standard (5-15MP)"},
                        {"value": "high", "label": "High Res (>15MP)"}
                    ]
                },
                "color": {
                    "label": "Color",
                    "options": [
                        {"value": "grayscale", "label": "Black & White"},
                        {"value": "transparent", "label": "Transparent"},
                        {"value": "red", "label": "Red"},
                        {"value": "orange", "label": "Orange"},
                        {"value": "yellow", "label": "Yellow"},
                        {"value": "green", "label": "Green"},
                        {"value": "turquoise", "label": "Turquoise"},
                        {"value": "blue", "label": "Blue"},
                        {"value": "lilac", "label": "Lilac"},
                        {"value": "pink", "label": "Pink"},
                        {"value": "white", "label": "White"},
                        {"value": "gray", "label": "Gray"},
                        {"value": "black", "label": "Black"},
                        {"value": "brown", "label": "Brown"}
                    ]
                }
            },
            "vector": {
                "orientation": {
                    "label": "Orientation",
                    "options": [
                        {"value": "horizontal", "label": "Landscape"},
                        {"value": "vertical", "label": "Portrait"},
                        {"value": "square", "label": "Square"}
                    ]
                },
                "size": {
                    "label": "Resolution",
                    "options": [
                        {"value": "web", "label": "Web (<5MP)"},
                        {"value": "standard", "label": "Standard (5-15MP)"},
                        {"value": "high", "label": "High Res (>15MP)"}
                    ]
                }
            },
            "illustration": {
                "orientation": {
                    "label": "Orientation",
                    "options": [
                        {"value": "horizontal", "label": "Landscape"},
                        {"value": "vertical", "label": "Portrait"},
                        {"value": "square", "label": "Square"}
                    ]
                },
                "size": {
                    "label": "Resolution",
                    "options": [
                        {"value": "web", "label": "Web (<5MP)"},
                        {"value": "standard", "label": "Standard (5-15MP)"},
                        {"value": "high", "label": "High Res (>15MP)"}
                    ]
                }
            },
            "music": {
                "duration": {
                    "label": "Duration",
                    "options": [
                        {"value": "short", "label": "Short (<30s)"},
                        {"value": "medium", "label": "Medium (30s-1.5min)"},
                        {"value": "long", "label": "Long (>1.5min)"}
                    ]
                },
                "tag": {
                    "label": "Tags",
                    "options": [
                        {"value": "ambient", "label": "Ambient"},
                        {"value": "chill", "label": "Chill"},
                        {"value": "classical", "label": "Classical"},
                        {"value": "electronic", "label": "Electronic"},
                        {"value": "energetic", "label": "Energetic"},
                        {"value": "jazz", "label": "Jazz"},
                        {"value": "loop", "label": "Loop"},
                        {"value": "piano", "label": "Piano"},
                        {"value": "relaxing", "label": "Relaxing"},
                        {"value": "synth", "label": "Synth"}
                    ]
                },
                "sort": {
                    "label": "Sort By",
                    "options": [
                        {"value": "rating", "label": "Highest Rated"},
                        {"value": "downloads", "label": "Most Popular"},
                        {"value": "date", "label": "Newest"}
                    ]
                }
            },
            "sfx": {
                "duration": {
                    "label": "Duration",
                    "options": [
                        {"value": "short", "label": "Short (<5s)"},
                        {"value": "medium", "label": "Medium (5-15s)"},
                        {"value": "long", "label": "Long (>15s)"}
                    ]
                },
                "tag": {
                    "label": "Tags",
                    "options": [
                        {"value": "ambience", "label": "Ambience"},
                        {"value": "click", "label": "Click"},
                        {"value": "explosion", "label": "Explosion"},
                        {"value": "foley", "label": "Foley"},
                        {"value": "impact", "label": "Impact"},
                        {"value": "mechanical", "label": "Mechanical"},
                        {"value": "nature", "label": "Nature"},
                        {"value": "voice", "label": "Voice"},
                        {"value": "water", "label": "Water"},
                        {"value": "whoosh", "label": "Whoosh"}
                    ]
                },
                "sort": {
                    "label": "Sort By",
                    "options": [
                        {"value": "rating", "label": "Highest Rated"},
                        {"value": "downloads", "label": "Most Popular"},
                        {"value": "date", "label": "Newest"}
                    ]
                }
            }
        }
    }
    
    # If specific asset type requested, return only that type's filters
    if asset_type:
        return {
            "primary": response["primary"],
            "assetFilters": response["assetFilters"].get(asset_type.lower(), {})
        }
    
    return response


# -----------------------------------
# Typo Correction / Query Enhancement
# -----------------------------------

# Common search terms dictionary (expandable)
COMMON_TERMS = {
    # Nature
    "mountain", "mountains", "ocean", "sea", "beach", "sunset", "sunrise", "forest", "tree", "trees",
    "flower", "flowers", "sky", "cloud", "clouds", "nature", "landscape", "river", "lake", "waterfall",
    "desert", "canyon", "valley", "hill", "grass", "field", "garden", "plant", "leaf", "leaves",
    
    # Urban
    "city", "building", "buildings", "street", "road", "car", "traffic", "architecture", "bridge",
    "downtown", "skyline", "urban", "town", "village", "house", "home",
    
    # People
    "person", "people", "man", "woman", "child", "children", "family", "business", "office", "work",
    "meeting", "team", "crowd", "face", "portrait", "smile", "hand", "hands", "foot", "feet",
    
    # Animals
    "dog", "cat", "bird", "fish", "horse", "animal", "animals", "wildlife", "pet",
    
    # Food
    "food", "meal", "coffee", "drink", "fruit", "vegetable", "breakfast", "lunch", "dinner",
    
    # Technology
    "computer", "laptop", "phone", "technology", "screen", "keyboard", "data", "code", "digital",
    
    # Abstract
    "light", "dark", "shadow", "color", "pattern", "texture", "background", "abstract", "design",
    "art", "creative", "modern", "vintage", "retro",
    
    # Music/Audio
    "music", "sound", "audio", "song", "melody", "beat", "rhythm", "piano", "guitar", "drum", "drums",
    "bass", "synth", "loop", "ambient", "electronic", "acoustic", "click", "beep", "notification"
}

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def correct_typo(query: str) -> str:
    """
    Attempt to correct typos in search query by finding closest matching common term.
    Returns corrected query if a close match is found, otherwise returns original.
    """
    words = query.lower().split()
    corrected_words = []
    
    for word in words:
        # Skip very short words or already correct words
        if len(word) <= 2 or word in COMMON_TERMS:
            corrected_words.append(word)
            continue
        
        # Find closest match in common terms
        best_match = word
        min_distance = float('inf')
        
        for term in COMMON_TERMS:
            # Only consider if word length is similar (within 2 characters)
            if abs(len(word) - len(term)) > 2:
                continue
            
            distance = levenshtein_distance(word, term)
            
            # If distance is small enough, it's likely a typo
            # Allow 1 typo for words 4-6 chars, 2 typos for words 7+ chars
            max_allowed = 1 if len(word) <= 6 else 2
            
            if distance < min_distance and distance <= max_allowed:
                min_distance = distance
                best_match = term
        
        corrected_words.append(best_match)
    
    corrected = " ".join(corrected_words)
    
    # Log if correction was made
    if corrected != query.lower():
        logger.info(f"🔧 Typo correction: '{query}' → '{corrected}'")
    
    return corrected


# -----------------------------------
# Embeddings / utils
# -----------------------------------

def get_embedding(text: str) -> List[float]:
    try:
        if not text.strip():
            return [0.0] * 1536

        res = openai_client.embeddings.create(
            model=OPENAI_EMBEDDINGS_MODEL,
            input=text,
        )
        return res.data[0].embedding

    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return [0.0] * 1536


def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = sqrt(sum(a * a for a in v1))
    n2 = sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0

    return dot / (n1 * n2)


# -----------------------------------
# FETCH + NORMALIZE + INDEX
# -----------------------------------

def fetch_and_index_all(
    query: str,
    limit: int = 15,  # Optimized for speed: 10-15 per provider
    provider_filter: Optional[str] = None,
    media_type: Optional[str] = None,
):

    docs = []
    provider_filter_lower = provider_filter.lower() if provider_filter else None

    use_pexels = provider_filter_lower in (None, "all", "pexels")
    use_pixabay = provider_filter_lower in (None, "all", "pixabay")
    use_freesound = provider_filter_lower in (None, "all", "freesound")
    use_unsplash = provider_filter_lower in (None, "all", "unsplash")

    fetch_videos = media_type is None or media_type.lower() in ("all", "video")
    fetch_photos = media_type is None or media_type.lower() in ("all", "photo")
    fetch_vectors = media_type is None or media_type.lower() in ("all", "vector")
    fetch_illustrations = media_type is None or media_type.lower() in ("all", "illustration")
    fetch_music = media_type is None or media_type.lower() in ("all", "music")
    fetch_sfx = media_type is None or media_type.lower() in ("all", "sfx")

    logger.info(f"📥 Fetching query='{query}', videos={fetch_videos}, photos={fetch_photos}, vectors={fetch_vectors}, illustrations={fetch_illustrations}, music={fetch_music}, sfx={fetch_sfx}")

    # --- PEXELS ---
    if use_pexels:
        if fetch_videos:
            try:
                raw = search_pexels_videos(query=query, limit=limit)
                for r in raw:
                    doc = normalize_pexels_video(r)
                    doc["provider"] = "pexels"
                    doc["type"] = "video"
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Pexels video error: {e}")

        if fetch_photos:
            try:
                raw = search_pexels_photos(query=query, limit=limit)
                for r in raw:
                    doc = normalize_pexels_photo(r)
                    doc["provider"] = "pexels"
                    doc["type"] = "photo"
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Pexels photo error: {e}")

    # --- PIXABAY ---
    if use_pixabay:
        if fetch_videos:
            try:
                raw = search_pixabay_videos(query=query, limit=limit)
                for r in raw:
                    doc = normalize_pixabay_video(r)
                    doc["provider"] = "pixabay"
                    doc["type"] = "video"
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Pixabay video error: {e}")

        if fetch_photos:
            try:
                raw = search_pixabay_photos(query=query, limit=limit)
                for r in raw:
                    doc = normalize_pixabay_photo(r)
                    doc["provider"] = "pixabay"
                    doc["type"] = "photo"
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Pixabay photo error: {e}")

        if fetch_vectors:
            try:
                raw = search_pixabay_vectors(query=query, limit=limit)
                for r in raw:
                    doc = normalize_pixabay_vector(r)
                    doc["provider"] = "pixabay"
                    doc["type"] = "vector"
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Pixabay vector error: {e}")

    # --- FREESOUND (SFX) ---
    if use_freesound:
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
        
        if fetch_music:
            try:
                raw = search_freesound_music(query=query, limit=limit)
                for r in raw:
                    doc = normalize_freesound_music(r)
                    doc["provider"] = "freesound"
                    doc["type"] = "music"
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Freesound music error: {e}")

    # --- UNSPLASH ---
    if use_unsplash and fetch_photos:
        try:
            raw = search_unsplash_photos(query=query, limit=limit)
            for r in raw:
                doc = normalize_unsplash_photo(r)
                doc["provider"] = "unsplash"
                doc["type"] = "photo"
                docs.append(doc)
        except Exception as e:
            logger.error(f"Unsplash error: {e}")
    
    # --- UNSPLASH ILLUSTRATIONS ---
    if use_unsplash and fetch_illustrations:
        try:
            # Search with "illustration" keyword appended
            illustration_query = f"{query} illustration" if query.lower() != "illustration" else query
            raw = search_unsplash_photos(query=illustration_query, limit=limit)
            for r in raw:
                doc = normalize_unsplash_photo(r)
                doc["provider"] = "unsplash"
                doc["type"] = "illustration"
                docs.append(doc)
        except Exception as e:
            logger.error(f"Unsplash illustration error: {e}")

    # --- ADD EMBEDDINGS + INDEX ---
    # DISABLED FOR DEMO: Skip embeddings & indexing to speed up search
    # if docs:
    #     logger.info(f"🤖 Generating embeddings for {len(docs)} docs...")
    #     for d in docs:
    #         title = d.get("title") or ""
    #         provider = d.get("provider", "")
    #         embed_text = f"{title} {provider}"
    #         d["embedding"] = get_embedding(embed_text)
    #
    #     try:
    #         index = meili_client.index(INDEX_NAME)
    #         index.add_documents(docs)
    #         logger.info(f"✅ Indexed {len(docs)} docs for '{query}'")
    #     except Exception as e:
    #         logger.error(f"Indexing error: {e}")
    # else:
    #     logger.warning(f"⚠️ No docs fetched for query '{query}'")

    logger.info(f"✅ Fetched {len(docs)} results for '{query}'")
    return docs


# -----------------------------------
# SIMPLE SEARCH + FILTERS
# -----------------------------------

@app.get("/search/simple")
def search_simple(
    response: Response,
    query: str = Query(...),
    provider: Optional[str] = Query(None),
    media_type: Optional[str] = Query(None, alias="type"),
    # Video filters
    aspect_ratio: Optional[str] = Query(None),
    resolution: Optional[str] = Query(None),
    # Photo/Vector filters
    orientation: Optional[str] = Query(None),  # horizontal, vertical, square
    color: Optional[str] = Query(None),  # Color filter for photos
    size: Optional[str] = Query(None),  # small, medium, large, xlarge
    # Audio filters (music/sfx)
    duration: Optional[str] = Query(None),  # short, medium, long (context-dependent)
    tag: Optional[str] = Query(None),  # genre/mood tags for music/sfx
    sort: Optional[str] = Query(None),  # rating, downloads, date
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
):
    """
    Fetch fresh results + apply CPU filters + paginate.
    """
    # Prevent caching to ensure fresh results with different filters
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    # Apply typo correction
    corrected_query = correct_typo(query)
    
    logger.info(f"🔍 SIMPLE search: '{query}' (provider={provider}, type={media_type}, orientation={orientation}, duration={duration}, size={size})")
    try:
        docs = fetch_and_index_all(
            query=corrected_query,
            limit=per_page * 3,
            provider_filter=provider,
            media_type=media_type,
        )

        # --- Aspect Ratio Filter ---
        if aspect_ratio:
            ar = aspect_ratio.lower().strip()
            filtered = []
            for d in docs:
                ori = (d.get("video_aspect_ratio") or "").lower()
                if ori == ar:
                    filtered.append(d)
            docs = filtered

        # --- Resolution Filter ---
        if resolution:
            res = resolution.lower().strip()
            docs = [
                d for d in docs
                if (d.get("video_resolution_label") or "").lower() == res
            ]

        # --- Orientation Filter (Photos/Vectors) ---
        if orientation:
            ori = orientation.lower().strip()
            docs = [
                d for d in docs
                if (d.get("photo_orientation") or "").lower() == ori
            ]

        # --- Color Filter (Photos) ---
        if color:
            col = color.lower().strip()
            docs = [
                d for d in docs
                if (d.get("photo_color") or "").lower() == col
            ]

        # --- Size Filter (Photos/Vectors) ---
        if size:
            sz = size.lower().strip()
            filtered = []
            for d in docs:
                w = d.get("width") or 0
                h = d.get("height") or 0
                megapixels = (w * h) / 1_000_000 if w and h else 0
                
                # Better categories based on actual photo usage
                if sz == "web" and megapixels < 5:
                    filtered.append(d)
                elif sz == "standard" and 5 <= megapixels < 15:
                    filtered.append(d)
                elif sz == "high" and megapixels >= 15:
                    filtered.append(d)
            docs = filtered

        # --- Duration Filter (Music/SFX) ---
        if duration:
            dur = duration.lower().strip()
            filtered = []
            for d in docs:
                dur_sec = d.get("duration_seconds") or d.get("duration") or 0
                asset_type = d.get("type") or ""
                
                # Different duration ranges for music vs SFX
                if asset_type in ["music"]:
                    # Music: short <30s, medium 30-90s, long >90s (more realistic for loops)
                    if dur == "short" and dur_sec < 30:
                        filtered.append(d)
                    elif dur == "medium" and 30 <= dur_sec <= 90:
                        filtered.append(d)
                    elif dur == "long" and dur_sec > 90:
                        filtered.append(d)
                elif asset_type in ["sfx"]:
                    # SFX: short <5s, medium 5-15s, long >15s
                    if dur == "short" and dur_sec < 5:
                        filtered.append(d)
                    elif dur == "medium" and 5 <= dur_sec < 15:
                        filtered.append(d)
                    elif dur == "long" and dur_sec >= 15:
                        filtered.append(d)
                else:
                    # Video duration filter (if needed)
                    if dur == "short" and dur_sec < 30:
                        filtered.append(d)
                    elif dur == "medium" and 30 <= dur_sec < 120:
                        filtered.append(d)
                    elif dur == "long" and dur_sec >= 120:
                        filtered.append(d)
            docs = filtered

        # --- Tag Filter (Music/SFX) ---
        if tag:
            tag_lower = tag.lower().strip()
            filtered = []
            for d in docs:
                tags_str = (d.get("tags") or "").lower()
                if tag_lower in tags_str:
                    filtered.append(d)
            docs = filtered

        # --- Sort Filter (Music/SFX) ---
        if sort:
            sort_by = sort.lower().strip()
            if sort_by == "rating":
                docs = sorted(docs, key=lambda x: x.get("avg_rating") or 0, reverse=True)
            elif sort_by == "downloads":
                docs = sorted(docs, key=lambda x: x.get("num_downloads") or 0, reverse=True)
            elif sort_by == "date":
                docs = sorted(docs, key=lambda x: x.get("created") or "", reverse=True)

        # Log filter results
        logger.info(f"📊 After filters: {len(docs)} results (aspect_ratio={aspect_ratio}, resolution={resolution}, orientation={orientation}, color={color}, size={size}, duration={duration}, tag={tag}, sort={sort})")

        if not docs:
            return {
                "mode": "simple",
                "results": [],
                "estimatedTotalHits": 0,
                "page": page,
                "per_page": per_page,
            }

        total_hits = len(docs)
        start = (page - 1) * per_page
        end = start + per_page
        page_docs = docs[start:end]

        results = []
        for d in page_docs:
            results.append({
                "id": d.get("id"),
                "provider": d.get("provider"),
                "title": d.get("title"),
                "preview_image_url": d.get("preview_image_url"),
                "video_url": d.get("video_url"),
                "audio_url": d.get("audio_url"),
                "page_url": d.get("page_url"),
                "type": d.get("type"),
                # Video fields
                "aspect_ratio": d.get("video_aspect_ratio"),
                "resolution": d.get("video_resolution_label"),
                # Photo/Vector fields
                "orientation": d.get("photo_orientation"),
                "color": d.get("photo_color"),
                # Common fields
                "width": d.get("width"),
                "height": d.get("height"),
                "duration": d.get("duration"),
                "duration_seconds": d.get("duration_seconds"),
                # Audio fields
                "tags": d.get("tags"),
                "license": d.get("license"),
                "avg_rating": d.get("avg_rating"),
                "num_downloads": d.get("num_downloads"),
                "num_ratings": d.get("num_ratings"),
                "created": d.get("created"),
            })

        logger.info(f"✅ Returning {len(results)} results (page {page}/{(total_hits + per_page - 1) // per_page})")
        
        result_response = {
            "mode": "simple",
            "query": query,
            "results": results,
            "estimatedTotalHits": total_hits,
            "page": page,
            "per_page": per_page,
            "timestamp": datetime.utcnow().isoformat() + "Z",  # Add timestamp for cache debugging
        }
        
        # Add corrected query if typo was fixed
        if corrected_query != query.lower():
            result_response["correctedQuery"] = corrected_query
        
        return result_response

    except Exception as e:
        logger.error(f"❌ SIMPLE ERROR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# SMART / SEMANTIC / HYBRID
# (for now: wrappers - all use simple search since embeddings are disabled)
# -----------------------------------

@app.get("/search/smart")
def search_smart(
    query: str = Query(...),
    provider: Optional[str] = Query(None),
    media_type: Optional[str] = Query(None, alias="type"),
    aspect_ratio: Optional[str] = Query(None),
    resolution: Optional[str] = Query(None),
    orientation: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    duration: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
):
    """Smart search - currently uses simple search (embeddings disabled for demo)"""
    # Create Response object for cache headers
    from fastapi import Response as ResponseClass
    temp_response = ResponseClass()
    result = search_simple(
        response=temp_response,
        query=query,
        provider=provider,
        media_type=media_type,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        orientation=orientation,
        color=color,
        size=size,
        duration=duration,
        tag=tag,
        sort=sort,
        page=page,
        per_page=per_page,
    )
    result["mode"] = "smart"
    return result


@app.get("/search/semantic")
def search_semantic(
    query: str = Query(...),
    provider: Optional[str] = Query(None),
    media_type: Optional[str] = Query(None, alias="type"),
    aspect_ratio: Optional[str] = Query(None),
    resolution: Optional[str] = Query(None),
    orientation: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    duration: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
):
    """Semantic search - currently uses simple search (embeddings disabled for demo)"""
    # Create Response object for cache headers
    from fastapi import Response as ResponseClass
    temp_response = ResponseClass()
    result = search_simple(
        response=temp_response,
        query=query,
        provider=provider,
        media_type=media_type,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        orientation=orientation,
        color=color,
        size=size,
        duration=duration,
        tag=tag,
        sort=sort,
        page=page,
        per_page=per_page,
    )
    result["mode"] = "semantic"
    return result


@app.get("/search/hybrid")
def search_hybrid(
    query: str = Query(...),
    provider: Optional[str] = Query(None),
    media_type: Optional[str] = Query(None, alias="type"),
    aspect_ratio: Optional[str] = Query(None),
    resolution: Optional[str] = Query(None),
    orientation: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    duration: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
):
    """Hybrid search - currently uses simple search (embeddings disabled for demo)"""
    # Create Response object for cache headers
    from fastapi import Response as ResponseClass
    temp_response = ResponseClass()
    result = search_simple(
        response=temp_response,
        query=query,
        provider=provider,
        media_type=media_type,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        orientation=orientation,
        color=color,
        size=size,
        duration=duration,
        tag=tag,
        sort=sort,
        page=page,
        per_page=per_page,
    )
    result["mode"] = "hybrid"
    return result


# -----------------------------------
# CLEANUP / CLEARING ENDPOINTS
# -----------------------------------

@app.get("/health")
def health_check():
    try:
        ms_ok = meili_client.is_healthy()
        openai_ok = False
        try:
            openai_client.models.list()
            openai_ok = True
        except:
            pass

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "meilisearch": ms_ok,
            "openai": openai_ok,
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/")
def root():
    return {"message": "OpenFootage API running"}
