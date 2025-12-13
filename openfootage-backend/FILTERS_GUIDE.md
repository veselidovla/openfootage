# Asset Type Filters Guide

## Overview
Each asset type (video, photo, vector, music, sfx) has dedicated filters that apply when that type is selected. Filters are applied **client-side after fetching** to enable instant filtering without additional API calls.

## 🎬 Video Filters

### Aspect Ratio
- **Values**: `16:9`, `9:16`, `1:1`, `4:3`, `other`
- **Example**: `?type=video&aspect_ratio=16:9`
- **Use Case**: Filter landscape, portrait, or square videos

### Resolution
- **Values**: `4k+`, `4k`, `full hd`, `hd`, `sd`
- **Breakdown**:
  - `4k+` = 2160p or higher
  - `4k` = 1440p to 2159p
  - `full hd` = 1080p to 1439p
  - `hd` = 720p to 1079p
  - `sd` = below 720p
- **Example**: `?type=video&resolution=4k%2B`

### Duration (Optional for videos)
- **Values**: `short`, `medium`, `long`
- **Breakdown**:
  - `short` = <30 seconds
  - `medium` = 30-120 seconds
  - `long` = >120 seconds
- **Example**: `?type=video&duration=short`

## 📸 Photo Filters

### Orientation
- **Values**: `horizontal`, `vertical`, `square`
- **Example**: `?type=photo&orientation=vertical`
- **Use Case**: Filter by photo orientation/shape

### Size (Megapixels)
- **Values**: `small`, `medium`, `large`, `xlarge`
- **Breakdown**:
  - `small` = <2 megapixels
  - `medium` = 2-8 megapixels
  - `large` = 8-20 megapixels
  - `xlarge` = >20 megapixels
- **Example**: `?type=photo&size=xlarge`
- **Use Case**: Filter by image resolution/quality

### Color
- **Values**: `grayscale`, `transparent`, `red`, `orange`, `yellow`, `green`, `turquoise`, `blue`, `lilac`, `pink`, `white`, `gray`, `black`, `brown`
- **Example**: `?type=photo&color=blue`
- **Use Case**: Find photos with dominant color
- **Note**: Currently only works for Pixabay photos

## 🎨 Vector Filters

### Orientation
- **Values**: `horizontal`, `vertical`, `square`
- **Example**: `?type=vector&orientation=horizontal`

### Size (Megapixels)
- **Values**: `small`, `medium`, `large`, `xlarge`
- **Example**: `?type=vector&size=large`

## 🎵 Music Filters

### Duration
- **Values**: `short`, `medium`, `long`
- **Breakdown**:
  - `short` = <60 seconds (~1 minute)
  - `medium` = 60-180 seconds (1-3 minutes)
  - `long` = >180 seconds (>3 minutes)
- **Example**: `?type=music&duration=medium`
- **Use Case**: Find background music loops (short), full tracks (medium/long)

## 🔊 Sound Effects (SFX) Filters

### Duration
- **Values**: `quick`, `short`, `medium`, `long`
- **Breakdown**:
  - `quick` = <2 seconds
  - `short` = 2-5 seconds
  - `medium` = 5-15 seconds
  - `long` = >15 seconds
- **Example**: `?type=sfx&duration=quick`
- **Use Case**: UI sounds (quick), transitions (short), ambience (medium/long)

## 📊 Get Available Filters API

### Endpoint: GET `/filters`

Get filter metadata for building UI dynamically.

#### Get All Filters
```bash
curl "http://localhost:8000/filters"
```

**Response**:
```json
{
  "video": {
    "aspect_ratio": {
      "label": "Aspect Ratio",
      "options": [
        {"value": "16:9", "label": "16:9 (Landscape)"},
        {"value": "9:16", "label": "9:16 (Portrait)"},
        ...
      ]
    },
    ...
  },
  "photo": { ... },
  "vector": { ... },
  "music": { ... },
  "sfx": { ... }
}
```

#### Get Filters for Specific Type
```bash
curl "http://localhost:8000/filters?type=photo"
```

**Response**:
```json
{
  "orientation": {
    "label": "Orientation",
    "options": [
      {"value": "horizontal", "label": "Horizontal"},
      {"value": "vertical", "label": "Vertical"},
      {"value": "square", "label": "Square"}
    ]
  },
  "size": { ... },
  "color": { ... }
}
```

## 🧪 Testing Examples

### Video - 4K Portrait
```bash
curl "http://localhost:8000/search/simple?query=city&type=video&aspect_ratio=9:16&resolution=4k%2B&per_page=10"
```

### Photo - Vertical XL Blue
```bash
curl "http://localhost:8000/search/simple?query=ocean&type=photo&orientation=vertical&size=xlarge&color=blue&per_page=10"
```

### Vector - Square Medium
```bash
curl "http://localhost:8000/search/simple?query=icon&type=vector&orientation=square&size=medium&per_page=10"
```

### Music - Medium Jazz
```bash
curl "http://localhost:8000/search/simple?query=jazz&type=music&duration=medium&per_page=10"
```

### SFX - Quick UI Sounds
```bash
curl "http://localhost:8000/search/simple?query=click&type=sfx&duration=quick&per_page=10"
```

## 🎨 Frontend Integration

### Dynamic Filter UI

```javascript
// Fetch filters for current asset type
const response = await fetch(`/filters?type=${currentType}`);
const filters = await response.json();

// Build filter UI
Object.entries(filters).forEach(([key, config]) => {
  const select = document.createElement('select');
  select.name = key;
  
  config.options.forEach(opt => {
    const option = document.createElement('option');
    option.value = opt.value;
    option.textContent = opt.label;
    select.appendChild(option);
  });
  
  filterContainer.appendChild(select);
});
```

### Applying Filters

```javascript
// Build query with filters
const params = new URLSearchParams({
  query: searchQuery,
  type: currentType,
  per_page: 24
});

// Add active filters
if (selectedOrientation) params.append('orientation', selectedOrientation);
if (selectedSize) params.append('size', selectedSize);
if (selectedDuration) params.append('duration', selectedDuration);

// Fetch filtered results
const response = await fetch(`/search/simple?${params}`);
const data = await response.json();
```

### Filter Chip UI Example

```javascript
// Show active filters as chips
const activeFilters = {
  orientation: 'vertical',
  size: 'xlarge',
  color: 'blue'
};

Object.entries(activeFilters).forEach(([key, value]) => {
  const chip = `
    <div class="filter-chip">
      ${key}: ${value}
      <button onclick="removeFilter('${key}')">×</button>
    </div>
  `;
  filterChipsContainer.innerHTML += chip;
});
```

## 🔄 Multiple Filter Combinations

Filters can be combined:

```bash
# Video: 16:9, 4K+, Short
curl "http://localhost:8000/search/simple?query=drone&type=video&aspect_ratio=16:9&resolution=4k%2B&duration=short"

# Photo: Vertical, XL, Blue
curl "http://localhost:8000/search/simple?query=sky&type=photo&orientation=vertical&size=xlarge&color=blue"

# Music: Medium duration jazz
curl "http://localhost:8000/search/simple?query=jazz&type=music&duration=medium"
```

## 📝 Response Fields by Type

### Video Response
```json
{
  "id": "pexels-video-123",
  "type": "video",
  "aspect_ratio": "16:9",
  "resolution": "4K+",
  "width": 3840,
  "height": 2160,
  "duration": 15.5,
  "duration_seconds": 15,
  "video_url": "...",
  ...
}
```

### Photo Response
```json
{
  "id": "pixabay-photo-456",
  "type": "photo",
  "orientation": "vertical",
  "color": "blue",
  "width": 4000,
  "height": 6000,
  ...
}
```

### Vector Response
```json
{
  "id": "pixabay-vector-789",
  "type": "vector",
  "orientation": "square",
  "width": 1920,
  "height": 1920,
  ...
}
```

### Music/SFX Response
```json
{
  "id": "freesound-1011",
  "type": "music",
  "duration": 161.7,
  "duration_seconds": 161,
  "audio_url": "...",
  "tags": "jazz, loop, background",
  "license": "...",
  ...
}
```

## ⚠️ Important Notes

1. **Client-Side Filtering**: Filters are applied after fetching, so results are instant
2. **Empty Results**: If no matches, returns `{"results": [], "estimatedTotalHits": 0}`
3. **Case Insensitive**: All filter values are case-insensitive
4. **URL Encoding**: Use `%2B` for `+` in URLs (e.g., `4k%2B` for `4k+`)
5. **Provider Limitations**:
   - Color filter only works for Pixabay photos
   - Not all providers return all metadata
   - Duration available for Freesound audio and some videos

## 🐛 Troubleshooting

### Filter Not Working
1. Check if asset type is specified: `?type=photo`
2. Verify filter value is valid (check `/filters` endpoint)
3. Ensure URL encoding for special characters (`+` → `%2B`)

### Empty Results
- Try broadening search query
- Remove strict filters
- Check if data has the filtered field (e.g., color only on Pixabay)

### Wrong Duration Range
- Check asset type (music vs sfx have different ranges)
- Verify `duration_seconds` field is present in response
- Music: short<60, medium 60-180, long>180
- SFX: quick<2, short 2-5, medium 5-15, long>15

## 🚀 Future Enhancements

Potential filter additions:
- **Video**: FPS filter (24fps, 30fps, 60fps, 120fps)
- **Photo**: License type filter (CC0, CC BY, etc.)
- **Music**: BPM filter, Genre/mood tags
- **SFX**: Category filter (nature, UI, impact, etc.)
- **All**: Date added, Popularity/downloads
