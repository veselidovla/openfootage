def normalize_unsplash_photo(raw: dict) -> dict:
    """
    Normalize Unsplash photo data into the OpenFootage schema.
    API Docs: https://unsplash.com/documentation#get-a-photo
    """
    photo_id = raw.get("id")
    
    # URLs
    links = raw.get("links") or {}
    page_url = links.get("html")
    
    # Images - Unsplash provides multiple sizes
    urls = raw.get("urls") or {}
    preview = urls.get("regular") or urls.get("full") or urls.get("small")  # regular is ~1080px width
    
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
    
    # Description/tags
    description = raw.get("description") or raw.get("alt_description") or ""
    tags_list = raw.get("tags") or []
    tags = ", ".join([tag.get("title", "") for tag in tags_list if tag.get("title")])
    
    # User info for attribution
    user = raw.get("user") or {}
    photographer = user.get("name") or "Unsplash"
    photographer_url = user.get("links", {}).get("html", "")
    
    # Title - use description or photographer name
    title = description if description else f"Photo by {photographer}"
    
    return {
        "id": f"unsplash-photo-{photo_id}",
        "provider": "unsplash",
        "type": "photo",
        
        "title": title,
        "page_url": page_url,
        "preview_image_url": preview,
        
        "width": width,
        "height": height,
        "photo_orientation": orientation,
        "photo_color": "",  # Not implemented for POC
        
        # Unsplash-specific metadata
        "tags": tags,
        "photographer": photographer,
        "photographer_url": photographer_url,
        
        # unused video fields
        "fps": None,
        "duration": None,
        "video_url": None,
    }
