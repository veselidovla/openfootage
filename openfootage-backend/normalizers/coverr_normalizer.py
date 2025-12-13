def normalize_coverr_video(raw: dict) -> dict:
    """
    Normalize Coverr video data.
    """
    video_id = raw.get("id")
    title = raw.get("title") or "Coverr Video"
    page_url = raw.get("url")
    thumb = raw.get("thumbnail") or raw.get("poster")

    files = raw.get("video_urls") or raw.get("video_files") or []
    chosen = files[0] if files else {}

    video_url = chosen.get("url")
    width = int(chosen.get("width") or 0)
    height = int(chosen.get("height") or 0)
    duration = raw.get("duration")

    # aspect ratio
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
        else:
            aspect = "other"
    else:
        aspect = "other"

    # resolution
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

    return {
        "id": f"coverr-{video_id}",
        "provider": "coverr",
        "type": "video",

        "title": title,
        "page_url": page_url,
        "preview_image_url": thumb,
        "video_url": video_url,

        "width": width,
        "height": height,
        "duration": duration,
        "duration_seconds": duration,
        "fps": None,

        "video_aspect_ratio": aspect,
        "video_resolution_label": resolution,
    }
