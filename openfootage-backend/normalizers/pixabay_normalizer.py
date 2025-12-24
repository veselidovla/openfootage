def normalize_pixabay_video(raw: dict) -> dict:
    """
    Normalize Pixabay video asset.
    """
    video_id = raw.get("id")
    page_url = raw.get("pageURL")
    tags = raw.get("tags") or ""

    # -----------------------------
    # Choose best video file
    # -----------------------------
    videos = raw.get("videos") or {}
    best = (
        videos.get("large")
        or videos.get("medium")
        or videos.get("small")
        or {}
    )

    width = int(best.get("width") or 0)
    height = int(best.get("height") or 0)
    duration = raw.get("duration")

    # -----------------------------
    # Derived attributes
    # -----------------------------
    from math import isfinite
    aspect = "other"
    if width > 0 and height > 0:
        ratio = width / float(height)
        if 1.7 < ratio < 1.9:
            aspect = "16:9"
        elif 0.9 < ratio < 1.1:
            aspect = "1:1"
        elif 0.55 < ratio < 0.7:
            aspect = "9:16"
        elif 1.28 < ratio < 1.37:
            aspect = "4:3"

    if height >= 2160:
        resolution = "UHD"
    elif height >= 1440:
        resolution = "4K"
    elif height >= 1080:
        resolution = "Full HD"
    elif height >= 720:
        resolution = "HD"
    else:
        resolution = "SD"

    # Get proper video thumbnail (not user profile picture)
    # Pixabay video thumbnails are nested in the videos object for each size
    # Try to get thumbnail from the same quality level as the video we selected
    thumbnail_url = best.get("thumbnail")
    if not thumbnail_url:
        # Fallback: try other video sizes for thumbnail
        for size in ["large", "medium", "small", "tiny"]:
            if videos.get(size, {}).get("thumbnail"):
                thumbnail_url = videos.get(size, {}).get("thumbnail")
                break
    if not thumbnail_url:
        # Last resort fallback to userImageURL (profile picture)
        thumbnail_url = raw.get("userImageURL")
    
    return {
        "id": f"pixabay-{video_id}",
        "provider": "pixabay",
        "type": "video",

        "title": tags,
        "page_url": page_url,
        "preview_image_url": thumbnail_url,
        "video_url": best.get("url"),

        "width": width,
        "height": height,
        "duration": duration,
        "duration_seconds": duration,
        "fps": None,

        "video_aspect_ratio": aspect,
        "video_resolution_label": resolution,
    }
