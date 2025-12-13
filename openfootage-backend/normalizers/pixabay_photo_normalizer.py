def normalize_pixabay_photo(raw: dict) -> dict:
    """
    Normalize Pixabay photo data.
    """
    return _normalize_pixabay_image(raw, asset_type="photo")


def normalize_pixabay_vector(raw: dict) -> dict:
    """
    Normalize Pixabay vector data.
    Vectors use the same structure as photos.
    """
    return _normalize_pixabay_image(raw, asset_type="vector")


def _normalize_pixabay_image(raw: dict, asset_type: str = "photo") -> dict:
    """
    Internal function to normalize Pixabay photo/vector data.
    """
    photo_id = raw.get("id")
    page_url = raw.get("pageURL")
    tags = raw.get("tags") or ""

    width = int(raw.get("imageWidth") or 0)
    height = int(raw.get("imageHeight") or 0)

    # Orientation
    if width > height:
        orientation = "horizontal"
    elif height > width:
        orientation = "vertical"
    else:
        orientation = "square"

    # Use largeImageURL (1280px) for best quality, fallback to webformatURL (640px)
    # This provides better preview experience
    preview = raw.get("largeImageURL") or raw.get("webformatURL") or raw.get("previewURL")

    return {
        "id": f"pixabay-{asset_type}-{photo_id}",
        "provider": "pixabay",
        "type": asset_type,

        "title": tags,
        "page_url": page_url,
        "preview_image_url": preview,

        "width": width,
        "height": height,
        "photo_orientation": orientation,
        "photo_color": raw.get("color") or "",

        # Not a video
        "duration": None,
        "fps": None,
        "video_url": None,
    }
