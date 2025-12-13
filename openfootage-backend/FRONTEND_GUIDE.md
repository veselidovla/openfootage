# Frontend Implementation Guide - Multi-Asset Type Support

## Overview

The backend now supports **5 asset types**:
- `video` - Video clips
- `photo` - Photographs
- `vector` - Vector graphics/illustrations
- `music` - Music tracks (structure ready, API pending)
- `sfx` - Sound effects (structure ready, API pending)

---

## 1. Updated API Response Structure

### Endpoint
```
GET /search/simple?query={query}&type={type}&provider={provider}
```

### Query Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `query` | string | Search query |
| `type` | `all`, `video`, `photo`, `vector`, `music`, `sfx` | Filter by asset type |
| `provider` | `all`, `pexels`, `pixabay`, `coverr` | Filter by provider |
| `page` | number | Page number (default: 1) |
| `per_page` | number | Results per page (default: 24) |

### Response Format

```typescript
interface SearchResponse {
  mode: string;
  query: string;
  results: Asset[];
  estimatedTotalHits: number;
  page: number;
  per_page: number;
}

interface Asset {
  id: string;
  provider: 'pexels' | 'pixabay' | 'coverr';
  title: string;
  preview_image_url: string;
  page_url: string;
  type: 'video' | 'photo' | 'vector' | 'music' | 'sfx';
  
  // Video/Photo/Vector specific
  video_url?: string | null;
  width?: number | null;
  height?: number | null;
  
  // Video only
  aspect_ratio?: string | null;  // "16:9", "9:16", "1:1", "4:3", "other"
  resolution?: string | null;    // "4K+", "4K", "Full HD", "HD", "SD"
  
  // Audio specific (when available)
  audio_url?: string | null;
  duration?: number | null;
  duration_seconds?: number | null;
}
```

---

## 2. TypeScript Type Definitions

```typescript
// types.ts

export type AssetType = 'video' | 'photo' | 'vector' | 'music' | 'sfx';
export type Provider = 'pexels' | 'pixabay' | 'coverr';
export type AspectRatio = '16:9' | '9:16' | '1:1' | '4:3' | 'other';
export type Resolution = '4K+' | '4K' | 'Full HD' | 'HD' | 'SD';

export interface Asset {
  id: string;
  provider: Provider;
  title: string;
  preview_image_url: string;
  page_url: string;
  type: AssetType;
  
  // Optional fields depending on type
  video_url?: string | null;
  audio_url?: string | null;
  width?: number | null;
  height?: number | null;
  aspect_ratio?: AspectRatio | null;
  resolution?: Resolution | null;
  duration?: number | null;
  duration_seconds?: number | null;
}

export interface SearchResponse {
  mode: string;
  query: string;
  results: Asset[];
  estimatedTotalHits: number;
  page: number;
  per_page: number;
}
```

---

## 3. UI Components Implementation

### 3.1 Type Filter Component

```tsx
// TypeFilter.tsx
import { AssetType } from './types';

const TYPE_OPTIONS: { value: AssetType | 'all'; label: string; icon: string }[] = [
  { value: 'all', label: 'All', icon: '🎬' },
  { value: 'video', label: 'Videos', icon: '🎥' },
  { value: 'photo', label: 'Photos', icon: '📷' },
  { value: 'vector', label: 'Vectors', icon: '🎨' },
  { value: 'music', label: 'Music', icon: '🎵' },
  { value: 'sfx', label: 'SFX', icon: '🔊' },
];

export function TypeFilter({ 
  selected, 
  onChange 
}: { 
  selected: AssetType | 'all'; 
  onChange: (type: AssetType | 'all') => void;
}) {
  return (
    <div className="flex gap-2">
      {TYPE_OPTIONS.map(option => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={selected === option.value ? 'active' : ''}
        >
          <span>{option.icon}</span>
          <span>{option.label}</span>
        </button>
      ))}
    </div>
  );
}
```

### 3.2 Conditional Filters (Aspect Ratio & Resolution)

```tsx
// ConditionalFilters.tsx
import { AssetType, AspectRatio, Resolution } from './types';

const ASPECT_RATIOS: AspectRatio[] = ['16:9', '9:16', '1:1', '4:3', 'other'];
const RESOLUTIONS: Resolution[] = ['4K+', '4K', 'Full HD', 'HD', 'SD'];

export function ConditionalFilters({
  assetType,
  selectedAspectRatio,
  selectedResolution,
  onAspectRatioChange,
  onResolutionChange,
}: {
  assetType: AssetType | 'all';
  selectedAspectRatio: AspectRatio | null;
  selectedResolution: Resolution | null;
  onAspectRatioChange: (ar: AspectRatio | null) => void;
  onResolutionChange: (res: Resolution | null) => void;
}) {
  // Only show these filters for videos
  const showVideoFilters = assetType === 'video' || assetType === 'all';

  if (!showVideoFilters) return null;

  return (
    <div className="flex gap-4">
      {/* Aspect Ratio Filter */}
      <div>
        <label>Aspect Ratio</label>
        <select 
          value={selectedAspectRatio || ''} 
          onChange={(e) => onAspectRatioChange(e.target.value as AspectRatio || null)}
        >
          <option value="">All Ratios</option>
          {ASPECT_RATIOS.map(ar => (
            <option key={ar} value={ar}>{ar}</option>
          ))}
        </select>
      </div>

      {/* Resolution Filter */}
      <div>
        <label>Resolution</label>
        <select 
          value={selectedResolution || ''} 
          onChange={(e) => onResolutionChange(e.target.value as Resolution || null)}
        >
          <option value="">All Resolutions</option>
          {RESOLUTIONS.map(res => (
            <option key={res} value={res}>{res}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
```

### 3.3 Asset Card Component

```tsx
// AssetCard.tsx
import { Asset } from './types';

export function AssetCard({ asset }: { asset: Asset }) {
  const renderByType = () => {
    switch (asset.type) {
      case 'video':
      case 'photo':
      case 'vector':
        return (
          <div className="asset-card">
            <img 
              src={asset.preview_image_url} 
              alt={asset.title}
              className="thumbnail"
            />
            <div className="info">
              <h3>{asset.title}</h3>
              <div className="badges">
                <span className="type">{asset.type}</span>
                <span className="provider">{asset.provider}</span>
                {asset.resolution && <span className="resolution">{asset.resolution}</span>}
                {asset.aspect_ratio && <span className="ratio">{asset.aspect_ratio}</span>}
              </div>
            </div>
          </div>
        );

      case 'music':
      case 'sfx':
        return (
          <div className="audio-card">
            <div className="thumbnail">
              {asset.preview_image_url ? (
                <img src={asset.preview_image_url} alt={asset.title} />
              ) : (
                <div className="placeholder">
                  {asset.type === 'music' ? '🎵' : '🔊'}
                </div>
              )}
            </div>
            <div className="info">
              <h3>{asset.title}</h3>
              <div className="meta">
                {asset.duration && (
                  <span className="duration">{formatDuration(asset.duration)}s</span>
                )}
                <span className="provider">{asset.provider}</span>
              </div>
            </div>
            {/* Play button when audio_url is available */}
            {asset.audio_url && (
              <button className="play-btn">▶</button>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <a 
      href={asset.page_url} 
      target="_blank" 
      rel="noopener noreferrer"
      className="asset-link"
    >
      {renderByType()}
    </a>
  );
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

---

## 4. Search Logic with Instant Filtering

```tsx
// SearchPage.tsx
import { useState, useEffect } from 'react';
import { Asset, AssetType, AspectRatio, Resolution } from './types';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [assetType, setAssetType] = useState<AssetType | 'all'>('all');
  const [provider, setProvider] = useState<string>('all');
  
  // Instant filters (client-side)
  const [aspectRatio, setAspectRatio] = useState<AspectRatio | null>(null);
  const [resolution, setResolution] = useState<Resolution | null>(null);
  
  const [allResults, setAllResults] = useState<Asset[]>([]);
  const [filteredResults, setFilteredResults] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch from API when query/type/provider changes
  useEffect(() => {
    if (!query) return;
    
    const fetchResults = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          query,
          type: assetType,
          provider,
          per_page: '50',
        });
        
        const response = await fetch(`/api/search/simple?${params}`);
        const data = await response.json();
        
        setAllResults(data.results);
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query, assetType, provider]);

  // Apply instant filters (aspect ratio & resolution) on client side
  useEffect(() => {
    let filtered = [...allResults];

    // Filter by aspect ratio (videos only)
    if (aspectRatio) {
      filtered = filtered.filter(
        asset => asset.aspect_ratio === aspectRatio
      );
    }

    // Filter by resolution (videos only)
    if (resolution) {
      filtered = filtered.filter(
        asset => asset.resolution === resolution
      );
    }

    setFilteredResults(filtered);
  }, [allResults, aspectRatio, resolution]);

  return (
    <div>
      <SearchBar value={query} onChange={setQuery} />
      
      <TypeFilter selected={assetType} onChange={setAssetType} />
      
      <ConditionalFilters
        assetType={assetType}
        selectedAspectRatio={aspectRatio}
        selectedResolution={resolution}
        onAspectRatioChange={setAspectRatio}
        onResolutionChange={setResolution}
      />

      {loading ? (
        <Loader />
      ) : (
        <div className="results-grid">
          {filteredResults.map(asset => (
            <AssetCard key={asset.id} asset={asset} />
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 5. Current Status

### ✅ Fully Working
- **Videos** - Pexels, Pixabay, Coverr
- **Photos** - Pexels, Pixabay
- **Vectors** - Pixabay

### 🎵 Audio Support (SFX via Freesound)

**SFX is now integrated!** The backend uses Freesound API for sound effects.

**Setup required:**
1. Get free API key from https://freesound.org/apiv2/apply
2. Add to `.env` or `config.py`: `FREESOUND_API_KEY=your_key_here`
3. Restart backend

**Music:** Currently not integrated, but you can:
- Use Freesound (it has music too)
- Integrate Mixkit (https://mixkit.co/)
- Add YouTube Audio Library

### How to Handle Audio in UI

```tsx
const TYPE_OPTIONS = [
  { value: 'all', label: 'All', icon: '🎬', enabled: true },
  { value: 'video', label: 'Videos', icon: '🎥', enabled: true },
  { value: 'photo', label: 'Photos', icon: '📷', enabled: true },
  { value: 'vector', label: 'Vectors', icon: '🎨', enabled: true },
  { value: 'music', label: 'Music', icon: '🎵', enabled: false, badge: 'Soon' },
  { value: 'sfx', label: 'SFX', icon: '🔊', enabled: false, badge: 'Soon' },
];
```

---

## 6. Testing Examples

```bash
# Search all types
curl "http://localhost:8000/search/simple?query=nature"

# Search videos only
curl "http://localhost:8000/search/simple?query=ocean&type=video"

# Search vectors only
curl "http://localhost:8000/search/simple?query=abstract&type=vector"

# Search photos from Pexels
curl "http://localhost:8000/search/simple?query=sunset&type=photo&provider=pexels"
```

---

## 7. Key Points

1. **Instant Filtering**: Aspect ratio and resolution filters work instantly without new API calls
2. **Conditional UI**: Show video-specific filters only when viewing videos
3. **Type Safety**: Use TypeScript interfaces for better development experience
4. **Graceful Degradation**: Music/SFX structure is ready but won't return results until API is integrated
5. **Responsive Design**: Different card layouts for visual assets vs. audio assets

---

**Ready to implement! All backend changes are complete and tested.** 🚀
