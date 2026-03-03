import os

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_BASE_URL = "https://api.pexels.com"

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
PIXABAY_BASE_URL = "https://pixabay.com/api"

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_BASE_URL = "https://api.unsplash.com"

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY")
FREESOUND_BASE_URL = "https://freesound.org/apiv2"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDINGS_MODEL = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")

MEILISEARCH_URL = os.getenv("MEILISEARCH_URL")
MEILISEARCH_API_KEY = os.getenv("MEILISEARCH_API_KEY")
