import os
from dotenv import load_dotenv

load_dotenv()

MEILISEARCH_URL = os.getenv("MEILI_HOST", "http://127.0.0.1:7700")
MEILISEARCH_API_KEY = os.getenv("MEILI_API_KEY", "OPENFOOTAGE_LOCAL_KEY")

# Pexels config
PEXELS_API_KEY = "4yQedAZW3iw5suz9h0fsIeA1xJgLTAgdk1GfapzPzqKhywFiouSNVrFx"
PEXELS_BASE_URL = "https://api.pexels.com"

PIXABAY_API_KEY = "53409059-234004d6f00b5643679ef7745"
PIXABAY_BASE_URL = "https://pixabay.com/api"

OPENAI_API_KEY = "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"
OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-small"

COVERR_API_KEY = "57d3d21dce2b089260e0c44610823dba"
COVERR_BESE_URL = "https://api.coverr.co"

# Freesound config (for SFX and music)
FREESOUND_API_KEY = "uqVyaNI3ayDSu0B4o7l32AuwpoV6gpVd6Indniqt"

# Unsplash config
UNSPLASH_ACCESS_KEY = "8FeaRVko7HDSCmLVG1NvDJIm4NI3WRaTHW8Lf1HIg5A"
UNSPLASH_BASE_URL = "https://api.unsplash.com"