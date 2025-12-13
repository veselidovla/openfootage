# normalizers/freesound_normalizer.py

def normalize_freesound_sfx(raw: dict) -> dict:
    """
    Normalize Freesound sound data to OpenFootage schema.
    
    Freesound API returns:
    - id, name, description
    - previews (preview-hq-mp3, preview-lq-mp3, preview-hq-ogg, preview-lq-ogg)
    - duration (in seconds)
    - tags (list)
    - license (URL)
    - url (page URL)
    - images (waveform_m, waveform_l, spectral_m, spectral_l)
    """
    sfx_id = raw.get("id")
    name = raw.get("name") or "Untitled SFX"
    description = raw.get("description") or ""
    page_url = raw.get("url") or ""
    duration = float(raw.get("duration") or 0)
    
    # Get tags
    tags = raw.get("tags") or []
    tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
    
    # Get audio preview URL (prefer high quality mp3)
    previews = raw.get("previews") or {}
    audio_url = (
        previews.get("preview-hq-mp3") 
        or previews.get("preview-lq-mp3")
        or previews.get("preview-hq-ogg")
        or previews.get("preview-lq-ogg")
        or ""
    )
    
    # Get waveform/spectral image as preview
    images = raw.get("images") or {}
    preview_image = (
        images.get("waveform_m")
        or images.get("spectral_m")
        or images.get("waveform_l")
        or images.get("spectral_l")
        or ""
    )
    
    # Combine name and tags for title
    title = name if name else tags_str[:50]
    
    # Get popularity metrics for sorting
    avg_rating = float(raw.get("avg_rating") or 0)
    num_downloads = int(raw.get("num_downloads") or 0)
    num_ratings = int(raw.get("num_ratings") or 0)
    created = raw.get("created") or ""
    
    return {
        "id": f"freesound-{sfx_id}",
        "provider": "freesound",
        "type": "sfx",
        
        "title": title,
        "description": description,
        "page_url": page_url,
        "preview_image_url": preview_image,
        "audio_url": audio_url,
        
        "duration": duration,
        "duration_seconds": int(duration),
        "tags": tags_str,
        
        # License info
        "license": raw.get("license") or "",
        
        # Popularity metrics for sorting
        "avg_rating": avg_rating,
        "num_downloads": num_downloads,
        "num_ratings": num_ratings,
        "created": created,
        
        # Not applicable for audio
        "width": None,
        "height": None,
        "video_url": None,
        "fps": None,
        "video_aspect_ratio": None,
        "video_resolution_label": None,
    }


def normalize_freesound_music(raw: dict) -> dict:
    """
    Normalize Freesound music data to OpenFootage schema.
    
    Music uses the same API and schema as SFX, just different search terms.
    """
    result = normalize_freesound_sfx(raw)
    result["type"] = "music"  # Override type to 'music'
    return result
