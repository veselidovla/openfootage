def normalize_pexels_photo(raw: dict) -> dict:
    """
    Normalize Pexels photo data into the OpenFootage schema.
    """
    photo_id = raw.get("id")
    url = raw.get("url")
    src = raw.get("src") or {}

    # Dimensions
    width = int(raw.get("width") or 0)
    height = int(raw.get("height") or 0)

    # Orientation
    if width > height:
        orientation = "horizontal"
    elif height > width:
        orientation = "vertical"
    else:
        orientation = "square"

    # Title fallback
    photographer = raw.get("photographer") or "Pexels Photo"

    return {
        "id": f"pexels-photo-{photo_id}",
        "provider": "pexels",
        "type": "photo",

        "title": photographer,
        "page_url": url,
        "preview_image_url": src.get("large") or src.get("large2x") or src.get("original"),

        "width": width,
        "height": height,
        "photo_orientation": orientation,
        "photo_color": "",

        # unused video fields kept consistent
        "fps": None,
        "duration": None,
        "video_url": None,
    }
