# OpenFootage

**One search. Every free asset you need.**

OpenFootage is an open-source stock media search engine that aggregates 
video, photo, vector, illustration, music, and SFX results from multiple 
free providers into a single, fast interface.

🔗 **Live demo:** https://openfootage-demo.netlify.app/

---

## What it does

- Search across **Pexels, Pixabay, Unsplash, and Freesound** simultaneously
- Filter by aspect ratio, resolution, orientation, color, duration, tags, and more
- Supports 6 asset types: video, photo, vector, illustration, music, SFX
- Built-in typo correction
- Designed for motion designers, filmmakers, and content creators

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI (Railway) |
| Frontend | React + TypeScript (Netlify) |
| Search | Direct provider APIs (Meilisearch/OpenAI ready) |

Running cost: **$5/month**

---

## Project Status

This is a working demo. The foundation is solid and the provider 
pattern is easy to extend. Currently looking for a collaborator or 
technical co-founder to help grow it.

**What's built:**
- Unified search across 4 providers
- Full filter system
- 4 search modes (Simple, Smart, Semantic, Hybrid)
- Pagination, no-cache, clean API

**What's next:**
- More free providers, free to start
- Semantic search via embeddings (already plumbed in, needs budget)
- User accounts + favorites
- Creator upload system (long-term vision)

---

## Contributing

The provider pattern is simple — each new source needs just two files:
- `providers/sourcename_client.py` — API call
- `normalizers/sourcename_normalizer.py` — standardize the response

If you want to add a provider or improve the search, open an issue or PR.

---

## Contact

Built by a motion designer/filmmaker, not a developer.
Looking for collaborators — reach out via Issues or 
openfootage.demo@gmail.com
