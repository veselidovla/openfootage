# models/asset.py
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class AssetType(str, Enum):
    VIDEO = "video"
    PHOTO = "photo"
    AUDIO = "audio"
    VECTOR = "vector"
    TEMPLATE = "template"
    LOTTIE = "lottie"

class AssetSubtype(str, Enum):
    # Video/Photo
    VIDEO_CLIP = "video_clip"
    VIDEO_LOOP = "video_loop"
    VIDEO_TRANSITION = "video_transition"
    VIDEO_BACKGROUND = "video_background"
    PHOTO_STOCK = "photo_stock"
    PHOTO_TEXTURE = "photo_texture"
    
    # Audio
    MUSIC = "music"
    SFX = "sfx"
    LOOP = "loop"
    AMBIENT = "ambient"
    
    # Vector
    ILLUSTRATION = "illustration"
    ICON = "icon"
    LOGO = "logo"
    UI_KIT = "ui_kit"
    
    # Template
    AFTER_EFFECTS = "after_effects"
    PREMIERE_PRO = "premiere_pro"
    FIGMA = "figma"
    BLENDER = "blender"

class UnifiedAsset:
    """The core data model for ALL asset types"""
    
    def __init__(
        self,
        # Core fields (required for all assets)
        asset_id: str,
        asset_type: AssetType,
        subtype: AssetSubtype,
        title: str,
        description: str = "",
        keywords: List[str] = None,
        
        # Creator info
        creator_id: str = "",
        creator_name: str = "",
        license_type: str = "royalty_free",
        is_public: bool = True,
        
        # File info
        file_url: str = "",
        thumbnail_url: str = "",
        file_size_mb: float = 0,
        file_format: str = "",
        
        # Smart search fields
        mood: List[str] = None,
        style: List[str] = None,
        project_type: List[str] = None,
        color_palette: List[str] = None,
        conceptual_tags: List[str] = None,
        
        # Performance metrics
        download_count: int = 0,
        like_count: int = 0,
        view_count: int = 0,
        rating: float = 0.0,
        
        # Type-specific data (will be filled based on asset_type)
        type_data: Dict[str, Any] = None,
        
        # Embedding for semantic search
        embedding: List[float] = None,
    ):
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.subtype = subtype
        self.title = title
        self.description = description
        self.keywords = keywords or []
        
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.license_type = license_type
        self.is_public = is_public
        
        self.file_url = file_url
        self.thumbnail_url = thumbnail_url
        self.file_size_mb = file_size_mb
        self.file_format = file_format
        
        self.mood = mood or []
        self.style = style or []
        self.project_type = project_type or []
        self.color_palette = color_palette or []
        self.conceptual_tags = conceptual_tags or []
        
        self.download_count = download_count
        self.like_count = like_count
        self.view_count = view_count
        self.rating = rating
        
        self.type_data = type_data or {}
        self.embedding = embedding or []
        
        # System fields
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Meilisearch/JSON"""
        return {
            # Core fields
            "id": self.asset_id,
            "asset_type": self.asset_type.value,
            "subtype": self.subtype.value,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            
            # Creator
            "creator_id": self.creator_id,
            "creator_name": self.creator_name,
            "license_type": self.license_type,
            "is_public": self.is_public,
            
            # File info
            "file_url": self.file_url,
            "thumbnail_url": self.thumbnail_url,
            "file_size_mb": self.file_size_mb,
            "file_format": self.file_format,
            
            # Smart search
            "mood": self.mood,
            "style": self.style,
            "project_type": self.project_type,
            "color_palette": self.color_palette,
            "conceptual_tags": self.conceptual_tags,
            
            # Performance
            "download_count": self.download_count,
            "like_count": self.like_count,
            "view_count": self.view_count,
            "rating": self.rating,
            
            # Type-specific data
            "type_data": self.type_data,
            
            # Embedding
            "embedding": self.embedding,
            
            # System
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_existing_video(cls, existing_data: Dict) -> 'UnifiedAsset':
        """Convert your existing video/photo data to the new format"""
        # Extract provider from ID
        asset_id = existing_data.get("id", "")
        
        # Determine asset type
        asset_type = AssetType.VIDEO if existing_data.get("video_url") else AssetType.PHOTO
        
        # Determine subtype
        if asset_type == AssetType.VIDEO:
            subtype = AssetSubtype.VIDEO_CLIP
            file_format = existing_data.get("video_url", "").split(".")[-1] if "." in existing_data.get("video_url", "") else "mp4"
        else:
            subtype = AssetSubtype.PHOTO_STOCK
            file_format = "jpg"  # Default for photos
        
        # Build type-specific data
        type_data = {}
        if asset_type == AssetType.VIDEO:
            type_data = {
                "duration_seconds": existing_data.get("duration", 0),
                "resolution": existing_data.get("video_resolution_label", ""),
                "fps": 30,
                "has_alpha_channel": False,
                "shot_type": [],
                "main_subject": [],
                "contains_people": False,
                "contains_audio": True,
            }
        elif asset_type == AssetType.PHOTO:
            type_data = {
                "resolution": existing_data.get("photo_resolution", ""),
                "orientation": existing_data.get("photo_orientation", "landscape"),
                "color_dominant": existing_data.get("photo_color", ""),
            }
        
        # Extract keywords from tags if available
        keywords = []
        if existing_data.get("tags"):
            keywords = existing_data["tags"].split(",") if isinstance(existing_data["tags"], str) else existing_data["tags"]
        
        return cls(
            asset_id=asset_id,
            asset_type=asset_type,
            subtype=subtype,
            title=existing_data.get("title", "Untitled"),
            description=existing_data.get("description", ""),
            keywords=keywords,
            
            creator_id=existing_data.get("creator_id", ""),
            creator_name=existing_data.get("creator", ""),
            
            file_url=existing_data.get("video_url", existing_data.get("page_url", "")),
            thumbnail_url=existing_data.get("preview_image_url", ""),
            file_format=file_format,
            
            # Smart fields (we'll populate these later with AI)
            mood=[],
            style=[],
            project_type=[],
            color_palette=[],
            conceptual_tags=[],
            
            type_data=type_data,
            
            # Use existing embedding if available
            embedding=existing_data.get("embedding", []),
        )

# Type-specific data builders
def build_video_data(
    duration_seconds: float = 0,
    resolution: str = "",
    fps: int = 30,
    has_alpha_channel: bool = False,
    shot_type: List[str] = None,
    main_subject: List[str] = None,
    contains_people: bool = False,
    contains_audio: bool = True,
    transcript: str = "",
) -> Dict[str, Any]:
    return {
        "duration_seconds": duration_seconds,
        "resolution": resolution,
        "fps": fps,
        "has_alpha_channel": has_alpha_channel,
        "shot_type": shot_type or [],
        "main_subject": main_subject or [],
        "contains_people": contains_people,
        "contains_audio": contains_audio,
        "transcript": transcript,
    }

def build_audio_data(
    duration_seconds: float = 0,
    bpm: int = 0,
    key: str = "",
    genre: List[str] = None,
    instruments: List[str] = None,
    tempo: str = "",  # slow, medium, fast
    loopable: bool = False,
    is_stem: bool = False,
    is_royalty_free: bool = True,
) -> Dict[str, Any]:
    return {
        "duration_seconds": duration_seconds,
        "bpm": bpm,
        "key": key,
        "genre": genre or [],
        "instruments": instruments or [],
        "tempo": tempo,
        "loopable": loopable,
        "is_stem": is_stem,
        "is_royalty_free": is_royalty_free,
    }

def build_vector_data(
    layers: int = 1,
    is_layered: bool = True,
    file_types: List[str] = None,  # svg, ai, eps, pdf
    colors: List[str] = None,
    is_scalable: bool = True,
    compatible_with: List[str] = None,  # illustrator, figma, sketch
    has_text: bool = False,
) -> Dict[str, Any]:
    return {
        "layers": layers,
        "is_layered": is_layered,
        "file_types": file_types or [],
        "colors": colors or [],
        "is_scalable": is_scalable,
        "compatible_with": compatible_with or [],
        "has_text": has_text,
    }