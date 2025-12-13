"""
Audio Normalizers (Music & SFX)

IMPORTANT: Pixabay does NOT provide an audio API.
Their API only supports images (photos/vectors) and videos.

These normalizers are prepared for alternative audio providers:
- Freesound API (https://freesound.org/docs/api/) - Free sound effects
- Mixkit API (https://mixkit.co/) - Free music & SFX
- YouTube Audio Library - Royalty-free music

The schema is defined and ready to integrate with any audio provider.
"""


def normalize_pixabay_music(raw: dict) -> dict:
    """
    Normalize Pixabay music data.
    
    Expected raw fields (when API is available):
    - id
    - title or name
    - pageURL
    - duration (in seconds)
    - previewURL (thumbnail)
    - downloadURL or audioURL
    - tags, genre, bpm, etc.
    """
    music_id = raw.get("id")
    title = raw.get("title") or raw.get("name") or "Untitled Music"
    page_url = raw.get("pageURL") or ""
    preview = raw.get("previewURL") or raw.get("thumbnail") or ""
    duration = raw.get("duration") or 0
    audio_url = raw.get("downloadURL") or raw.get("audioURL") or ""
    tags = raw.get("tags") or ""
    
    return {
        "id": f"pixabay-music-{music_id}",
        "provider": "pixabay",
        "type": "music",
        
        "title": title,
        "page_url": page_url,
        "preview_image_url": preview,
        "audio_url": audio_url,
        
        "duration": duration,
        "duration_seconds": duration,
        "tags": tags,
        
        # Audio-specific metadata (when available)
        "genre": raw.get("genre") or "",
        "bpm": raw.get("bpm"),
        "mood": raw.get("mood") or "",
        
        # Not applicable for audio
        "width": None,
        "height": None,
        "video_url": None,
        "fps": None,
    }


def normalize_pixabay_sfx(raw: dict) -> dict:
    """
    Normalize Pixabay sound effects data.
    
    SFX have similar structure to music but different use case.
    """
    sfx_id = raw.get("id")
    title = raw.get("title") or raw.get("name") or "Untitled SFX"
    page_url = raw.get("pageURL") or ""
    preview = raw.get("previewURL") or raw.get("thumbnail") or ""
    duration = raw.get("duration") or 0
    audio_url = raw.get("downloadURL") or raw.get("audioURL") or ""
    tags = raw.get("tags") or ""
    
    return {
        "id": f"pixabay-sfx-{sfx_id}",
        "provider": "pixabay",
        "type": "sfx",
        
        "title": title,
        "page_url": page_url,
        "preview_image_url": preview,
        "audio_url": audio_url,
        
        "duration": duration,
        "duration_seconds": duration,
        "tags": tags,
        
        # SFX-specific metadata
        "category": raw.get("category") or "",
        
        # Not applicable for audio
        "width": None,
        "height": None,
        "video_url": None,
        "fps": None,
    }
