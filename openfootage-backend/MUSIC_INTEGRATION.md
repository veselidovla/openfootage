# Music Integration - Freesound

## Overview
Music search is now integrated using **Freesound API**. The backend searches for music loops, beats, and instrumental tracks when `type=music` is specified.

## Provider Research
We evaluated three free music providers:

### ❌ Pixabay Music (190,000+ tracks)
- **Issue**: No API endpoint despite having music on website
- **Status**: Website has music at https://pixabay.com/music/ but `/api/music/` endpoint doesn't exist
- **Alternative Use**: Already integrated for videos, photos, and vectors

### ❌ Mixkit (200+ curated tracks)
- **Issue**: No public API, only web scraping possible
- **Status**: Royalty-free, no attribution, but too small collection and no API
- **URL**: https://mixkit.co/free-stock-music/

### ✅ Freesound (7,500+ music tracks)
- **Chosen Solution**: Already configured with API key
- **Collection**: 7,518 results for "piano music", thousands more for other genres
- **API**: Same endpoint as SFX, just different query terms
- **License**: Creative Commons (varies by track, check `license` field)
- **URL**: https://freesound.org/apiv2/

## Implementation

### 1. Search Function (`providers/freesound_client.py`)
```python
def search_freesound_music(query: str, limit: int = 25) -> List[dict]:
    """
    Search Freesound for music tracks.
    
    Appends 'music' to query to find musical content vs sound effects.
    Returns same schema as SFX search.
    """
    music_query = f"{query} music"
    # ... API call with timeout=4s
```

**Query Strategy**: Appends "music" to user query (e.g., "piano" → "piano music") to filter musical content.

### 2. Normalizer (`normalizers/freesound_normalizer.py`)
```python
def normalize_freesound_music(raw: dict) -> dict:
    """
    Normalize Freesound music data.
    Reuses SFX normalizer since API schema is identical.
    """
    result = normalize_freesound_sfx(raw)
    result["type"] = "music"  # Override type
    return result
```

### 3. Integration (`main.py`)
```python
# In fetch_and_index_all():
if use_freesound and fetch_music:
    raw = search_freesound_music(query=query, limit=limit)
    for r in raw:
        doc = normalize_freesound_music(r)
        doc["provider"] = "freesound"
        doc["type"] = "music"
        docs.append(doc)
```

## API Response Schema

Music results include these fields:

```json
{
  "id": "freesound-320603",
  "provider": "freesound",
  "type": "music",
  "title": "Ambient Piano Music #4",
  "description": "...",
  "page_url": "https://freesound.org/people/benpm/sounds/320603/",
  "preview_image_url": "https://cdn.freesound.org/displays/320/320603_2594536_wave_M.png",
  "audio_url": "https://cdn.freesound.org/previews/320/320603_2594536-hq.mp3",
  "duration": 96.0,
  "duration_seconds": 96,
  "tags": "ambient, atmosphere, electronic, improvised, loop, music, piano, soft",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "width": null,
  "height": null,
  "video_url": null,
  "aspect_ratio": null,
  "resolution": null
}
```

### Audio-Specific Fields:
- `audio_url`: Direct link to HQ MP3 preview (~128kbps)
- `preview_image_url`: Waveform or spectrogram image
- `duration`: Duration in seconds (float)
- `duration_seconds`: Duration as integer
- `tags`: Comma-separated keywords

## Usage Examples

### Search for Music
```bash
# Piano music
curl "http://localhost:8000/search/simple?query=piano&type=music&per_page=5"

# Jazz music
curl "http://localhost:8000/search/simple?query=jazz&type=music&per_page=5"

# Ambient music
curl "http://localhost:8000/search/simple?query=ambient&type=music&per_page=5"

# Electronic music
curl "http://localhost:8000/search/simple?query=electronic&type=music&per_page=5"
```

### Mixed Search (Music + SFX + Videos)
```bash
# Search all types
curl "http://localhost:8000/search/simple?query=rain&type=all"

# Search only audio (music + sfx)
curl "http://localhost:8000/search/simple?query=rain" # defaults to all types
```

## Test Results

### ✅ Verified Queries
- **Piano**: 3 results - "Ambient Piano Music #4", "#3", "#1"
- **Jazz**: 6 results - "Relaxing Jazz Music (loop)", "Jazz Background Music Loop"
- **Electronic**: 3+ results - Various electronic music loops
- **Ambient**: 2 results - "Ambient Piano Music #4", "#3"

### Performance
- **Timeout**: 4 seconds per request (same as other providers)
- **Limit**: 25 results per request (configurable)
- **Response Time**: ~500-800ms typical

## Licensing

Freesound content uses Creative Commons licenses:
- Most common: **CC BY** (attribution required)
- Some: **CC0** (public domain, no attribution)
- Check `license` field in each result

**Important**: Each track has its own license. Display the license URL to users:
```javascript
// Frontend should show
<a href={result.license}>License: {result.license}</a>
```

## Frontend Integration

### Display Music Cards
```javascript
if (result.type === 'music') {
  return (
    <MusicCard
      title={result.title}
      waveform={result.preview_image_url}  // Waveform image
      audioUrl={result.audio_url}          // For audio player
      duration={result.duration_seconds}   // Show duration
      tags={result.tags}                   // Show tags
      license={result.license}             // Link to license
      provider="Freesound"
    />
  );
}
```

### Audio Player Integration
```javascript
<audio controls>
  <source src={result.audio_url} type="audio/mpeg" />
</audio>
```

### Duration Formatting
```javascript
const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};
```

## API Configuration

The API key is already configured in `config.py`:
```python
FREESOUND_API_KEY = "uqVyaNI3ayDSu0B4o7l32AuwpoV6gpVd6Indniqt"
```

This key is used for both SFX and music searches.

## Debug Logs

Music searches log debug info:
```
[DEBUG] Freesound MUSIC request URL: https://freesound.org/apiv2/search/text/?query=piano+music&token=...
[DEBUG] Freesound MUSIC totalHits for 'piano': 7518 (returned: 25)
```

## Known Limitations

1. **Query Dependency**: Music quality depends on Freesound's tagging
2. **Creative Commons**: Most tracks require attribution (check license field)
3. **Preview Only**: Audio URLs are 128kbps MP3 previews, not full quality
4. **No Filtering**: Can't filter by BPM, key, mood, etc. (Freesound API limitation)

## Future Enhancements

Potential improvements:
1. **Advanced Filters**: Add duration filter (e.g., `duration:[30 TO 120]` for 30s-2min tracks)
2. **BPM Search**: Use Freesound's `filter` parameter for BPM ranges
3. **Tag Filtering**: Filter by tags like "loop", "beat", "instrumental"
4. **Pagination**: Implement page navigation for more results
5. **Alternative Providers**: Consider adding YouTube Audio Library or Free Music Archive if needed

## Troubleshooting

### No Results
- Check if query is too specific
- Try broader terms: "ambient" → "ambient music"
- Verify API key is set: `echo $FREESOUND_API_KEY` or check `config.py`

### Timeout Errors
- Current timeout: 4 seconds
- Increase in `providers/freesound_client.py` if needed

### Audio Preview Not Playing
- Check CORS settings in `main.py`
- Verify `audio_url` field is present in response
- Test audio URL directly in browser

## Related Documentation
- [FREESOUND_SETUP.md](./FREESOUND_SETUP.md) - API setup guide
- [AUDIO_INTEGRATION_GUIDE.md](./AUDIO_INTEGRATION_GUIDE.md) - SFX + Music integration
- [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md) - Frontend display examples
