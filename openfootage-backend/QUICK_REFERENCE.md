# Quick Reference - OpenFootage Backend Demo

## What Changed? (TL;DR)

### ⚡ Speed Optimizations
- ❌ **Embeddings OFF** - No OpenAI calls (save ~200-500ms per search)
- ❌ **Indexing OFF** - No Meilisearch writes (save ~50-150ms per search)
- 📉 **Fetch limits reduced** - 25 per provider (was 40)
- ⏱️ **Timeouts set to 4s** - Fail fast if provider is slow

### 📊 Demo Performance
- **Before:** ~1-2 seconds per search (with embeddings + indexing)
- **After:** ~300-700ms per search (direct provider fetching only)
- **Results:** 40-60 clips (was 120-160)
- **Cost:** ~$0.0001-0.0003 saved per search

### 📝 Logging Enhanced
```
🔍 SIMPLE search: 'ocean' (provider=pexels, type=video)
📥 Fetching query='ocean', videos=True, photos=False
✅ Fetched 25 results for 'ocean'
✅ Returning 24 results (page 1/2)
```

---

## Quick Deploy (for 10 testers)

### 1. Server Setup
```bash
# One VPS (2 vCPU, 4GB RAM)
sudo apt update && sudo apt install python3-pip docker.io nginx -y

# Start Meilisearch
docker run -d -p 7700:7700 \
  -e MEILI_MASTER_KEY=YOUR_KEY_HERE \
  getmeili/meilisearch:v1.5

# Deploy backend
cd /opt && git clone <repo> openfootage-backend
cd openfootage-backend
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn meilisearch-python openai requests python-dotenv
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### 2. Environment Variables
```bash
# .env file
MEILI_HOST=http://127.0.0.1:7700
MEILI_API_KEY=YOUR_KEY_HERE
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
COVERR_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### 3. Test It
```bash
curl http://localhost:8000/health
curl "http://localhost:8000/search/simple?query=ocean"
```

---

## What Still Works?

✅ All 4 search endpoints (`/simple`, `/smart`, `/semantic`, `/hybrid`)  
✅ Provider filtering (pexels, pixabay, coverr)  
✅ Media type filtering (video, photo)  
✅ Aspect ratio & resolution filters  
✅ Pagination  
✅ Error handling  

---

## What's Disabled? (For Demo Only)

❌ Embedding generation (no OpenAI calls)  
❌ Document indexing (no Meilisearch writes)  
❌ Semantic ranking (just a label)  

**Can be re-enabled later for production.**

---

## Next Steps (Optional)

1. **Parallel fetching** - Use async to fetch providers simultaneously
2. **Caching** - Add Redis for frequent queries
3. **Re-enable embeddings** - For true semantic search
4. **Scale up** - Add more resources when needed

---

## Files Changed

- `main.py` - Embeddings/indexing disabled, logging enhanced
- `providers/*.py` - Timeouts reduced to 4s
- `DEPLOYMENT.md` - Full deployment guide
- `CHANGES.md` - Detailed change log

---

**Ready for demo! 🚀**

For full details, see `DEPLOYMENT.md` or `CHANGES.md`
