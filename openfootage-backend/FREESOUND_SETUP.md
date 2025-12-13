# Freesound SFX Integration - Setup Guide

## ✅ Implementation Complete!

Sound effects (SFX) are now integrated via **Freesound API**.

---

## Quick Setup (3 minutes)

### Step 1: Get Freesound API Key (FREE)

1. Go to https://freesound.org/apiv2/apply
2. Register or login to Freesound
3. Fill out the simple application form
4. You'll receive your API key instantly

### Step 2: Add API Key to Config

**Option A: Environment Variable (Recommended)**
```bash
# Add to .env file
FREESOUND_API_KEY=your_key_here
```

**Option B: Direct in config.py**
```python
FREESOUND_API_KEY = "your_key_here"
```

### Step 3: Restart Backend

```bash
# If running with uvicorn
uvicorn main:app --reload
```

### Step 4: Test It!

```bash
# Search for explosion sounds
curl "http://localhost:8000/search/simple?query=explosion&type=sfx"

# Search for dog barking
curl "http://localhost:8000/search/simple?query=dog+bark&type=sfx"

# Search for rain sounds
curl "http://localhost:8000/search/simple?query=rain&type=sfx"
```

---

## What You Get

Each SFX result includes:

```json
{
  "id": "freesound-12345",
  "provider": "freesound",
  "type": "sfx",
  "title": "Explosion Sound",
  "description": "Loud explosion with reverb",
  "preview_image_url": "https://freesound.org/.../waveform_m.png",
  "audio_url": "https://freesound.org/.../preview-hq-mp3.mp3",
  "page_url": "https://freesound.org/people/user/sounds/12345/",
  "duration": 3.5,
  "duration_seconds": 3,
  "tags": "explosion, boom, impact",
  "license": "http://creativecommons.org/licenses/by/3.0/"
}
```

**Key Features:**
- ✅ Audio preview URL (high-quality MP3)
- ✅ Waveform/spectral image for visual preview
- ✅ Duration in seconds
- ✅ Tags for categorization
- ✅ Creative Commons license info
- ✅ Direct link to Freesound page

---

## Frontend Integration

### 1. SFX Card Component

```tsx
function SFXCard({ sfx }: { sfx: Asset }) {
  return (
    <div className="sfx-card">
      {/* Waveform preview */}
      {sfx.preview_image_url && (
        <img src={sfx.preview_image_url} alt={sfx.title} />
      )}
      
      {/* Title and duration */}
      <h3>{sfx.title}</h3>
      <span className="duration">{sfx.duration_seconds}s</span>
      
      {/* Audio player */}
      <audio controls src={sfx.audio_url}>
        Your browser does not support audio.
      </audio>
      
      {/* Tags */}
      <div className="tags">{sfx.tags}</div>
      
      {/* Provider badge */}
      <span className="provider">Freesound</span>
    </div>
  );
}
```

### 2. Enable SFX Filter

```tsx
const TYPE_OPTIONS = [
  { value: 'all', label: 'All', icon: '🎬', enabled: true },
  { value: 'video', label: 'Videos', icon: '🎥', enabled: true },
  { value: 'photo', label: 'Photos', icon: '📷', enabled: true },
  { value: 'vector', label: 'Vectors', icon: '🎨', enabled: true },
  { value: 'sfx', label: 'SFX', icon: '🔊', enabled: true }, // NOW ENABLED!
  { value: 'music', label: 'Music', icon: '🎵', enabled: false }, // Still coming soon
];
```

---

## API Response Examples

### Request
```bash
GET /search/simple?query=thunder&type=sfx&per_page=5
```

### Response
```json
{
  "mode": "simple",
  "query": "thunder",
  "results": [
    {
      "id": "freesound-123456",
      "provider": "freesound",
      "type": "sfx",
      "title": "Thunder Rumble",
      "audio_url": "https://freesound.org/.../preview-hq-mp3.mp3",
      "preview_image_url": "https://freesound.org/.../waveform_m.png",
      "duration_seconds": 5,
      "tags": "thunder, storm, weather"
    }
  ],
  "estimatedTotalHits": 150,
  "page": 1,
  "per_page": 5
}
```

---

## Freesound Features

### Huge Library
- 600,000+ sounds
- Community-contributed
- Professional quality

### Creative Commons Licensed
- Most sounds are free to use
- Attribution required (link to Freesound page)
- License info included in API response

### Rich Metadata
- Tags and descriptions
- Duration
- Quality ratings
- User info

### Multiple Formats
- High-quality MP3 previews
- OGG format also available
- Waveform and spectral images

---

## Troubleshooting

### No results showing up

1. **Check API key is set:**
   ```bash
   echo $FREESOUND_API_KEY
   ```

2. **Check backend logs:**
   ```bash
   tail -f logs.txt  # or wherever your logs are
   ```

3. **Test API directly:**
   ```bash
   curl "https://freesound.org/apiv2/search/text/?query=test&token=YOUR_KEY"
   ```

### "API key not set" error

Make sure you've added the key to either:
- `.env` file: `FREESOUND_API_KEY=your_key`
- `config.py`: `FREESOUND_API_KEY = "your_key"`

Then restart the backend.

---

## Rate Limits

**Freesound API limits:**
- 60 requests per minute
- 2000 requests per day

**Already optimized in backend:**
- 4-second timeout per request
- Max 25 results per search (configurable)
- Error handling prevents crashes

---

## What's Next?

### For Music Support
You can either:
1. Use Freesound (it has music too)
2. Integrate Mixkit (https://mixkit.co/)
3. Add YouTube Audio Library

See `AUDIO_INTEGRATION_GUIDE.md` for details.

---

**You're all set! SFX search is now fully functional.** 🎉

Test it: `curl "http://localhost:8000/search/simple?query=explosion&type=sfx"`
