def infer_video_aspect_ratio(width: int, height: int) -> str:
    """
    Return a canonical aspect ratio string based on width/height.
    """
    if width <= 0 or height <= 0:
        return "other"

    ratio = width / float(height)

    if 1.7 < ratio < 1.9:
        return "16:9"
    if 0.9 < ratio < 1.1:
        return "1:1"
    if 0.55 < ratio < 0.7:
        return "9:16"
    if 1.28 < ratio < 1.37:
        return "4:3"

    return "other"


def infer_video_resolution_label(height: int) -> str:
    """
    Bucket by vertical resolution into user-friendly labels.
    """
    if height >= 2160:
        return "UHD"        # 4K and above
    if height >= 1440:
        return "4K"         # ~4K-ish (1440p)
    if height >= 1080:
        return "Full HD"    # 1080p
    if height >= 720:
        return "HD"         # 720p
    return "SD"            # sub-720p


def normalize_pexels_video(raw: dict) -> dict:
    """
    Convert RAW Pexels video JSON into a unified OpenFootage document.
    """
    video_id = raw.get("id")
    url = raw.get("url")
    image = raw.get("image")

    # --------------------------------------------
    # Pick a 'best' file and extract width/height/FPS
    # --------------------------------------------
    video_files = raw.get("video_files") or []
    chosen = None

    if video_files:
        chosen = video_files[0]  # default
        for f in video_files:
            if f.get("quality") == "hd":
                chosen = f
                break

    chosen_file_url = chosen.get("link") if chosen else None

    # Width/Height from raw entry
    width = int(raw.get("width") or 0)
    height = int(raw.get("height") or 0)

    # Fallback: use first file dimensions
    if (not width or not height) and video_files:
        width = int(video_files[0].get("width") or width or 0)
        height = int(video_files[0].get("height") or height or 0)

    # --------------------------------------------
    # Extract FPS if available
    # --------------------------------------------
    fps = None
    for f in video_files:
        if "fps" in f and f["fps"]:
            fps = f["fps"]
            break

    # --------------------------------------------
    # Duration (in seconds)
    # --------------------------------------------
    raw_duration = raw.get("duration")
    try:
        duration_seconds = int(raw_duration) if raw_duration is not None else None
    except (TypeError, ValueError):
        duration_seconds = None

    # --------------------------------------------
    # Derive aspect ratio / resolution bucket
    # --------------------------------------------
    video_aspect_ratio = infer_video_aspect_ratio(width, height)
    video_resolution_label = infer_video_resolution_label(height)

    # --------------------------------------------
    # Title (fallback to author name)
    # --------------------------------------------
    user = raw.get("user") or {}
    title = user.get("name") or "Pexels Video"

    # --------------------------------------------
    # Final normalized document
    # --------------------------------------------
    return {
        "id": f"pexels-{video_id}",
        "provider": "pexels",
        "title": title,
        "page_url": url,
        "preview_image_url": image,
        "video_url": chosen_file_url,

        "width": width,
        "height": height,
        "duration": raw.get("duration"),   # raw original
        "duration_seconds": duration_seconds,

        "fps": fps,                        # ⭐ NEW
        "video_aspect_ratio": video_aspect_ratio,
        "video_resolution_label": video_resolution_label,
    }
