# Dynamic Filter Implementation Guide

## Overview
The frontend now supports **dynamic filters** that automatically adjust based on the selected asset type. Filters are fetched from the backend and rendered dynamically.

---

## 🎯 Features Implemented

### 1. **Dynamic Filter Fetching**
When a user selects an asset type, the frontend fetches available filters from:
```
GET /filters/{asset_type}
```

**Response Example:**
```json
{
  "asset_type": "video",
  "filters": [
    {
      "name": "aspect_ratio",
      "label": "Aspect Ratio",
      "type": "buttons",
      "options": [
        { "value": "16:9", "label": "16:9", "description": "Widescreen" },
        { "value": "9:16", "label": "9:16", "description": "Vertical" },
        { "value": "1:1", "label": "1:1", "description": "Square" }
      ]
    },
    {
      "name": "resolution",
      "label": "Resolution",
      "type": "select",
      "options": [
        { "value": "4k+", "label": "4K+", "description": "2160p+" },
        { "value": "4k", "label": "4K", "description": "1440p" },
        { "value": "fullhd", "label": "Full HD", "description": "1080p" }
      ]
    }
  ]
}
```

### 2. **Automatic Filter UI Rendering**
Filters are automatically rendered based on their type:
- **`type: "buttons"`** → Pill-style buttons
- **`type: "select"`** → Dropdown menu

### 3. **Instant Client-Side Filtering**
- Filters are applied **instantly** without making new API calls
- Uses `useMemo` for performance optimization
- Results update in real-time as filters change

### 4. **Active Filter Chips**
Visual chips showing currently applied filters:
- Display filter name and selected value
- Click **×** to remove individual filters
- **Clear all** button to reset all filters at once
- Smooth fade-in animation

### 5. **Filter Management Functions**
```typescript
handleFilterChange(filterName, value)  // Apply a filter
removeFilter(filterName)                // Remove a filter
clearAllFilters()                       // Reset all filters
```

### 6. **Results Count Display**
Shows filtering effects:
```
Showing 12 of 24 results (1,234 total available)
```

### 7. **Asset Type-Specific Filters**
Filters change automatically when switching asset types:

**Videos:**
- Aspect Ratio (16:9, 9:16, 1:1, 4:3, other)
- Resolution (4K+, 4K, Full HD, HD, SD)

**Photos:**
- Orientation (landscape, portrait, square)
- Size (large, medium, small)
- Color (specific colors)

**Vectors:**
- Orientation (horizontal, vertical, square)
- Size (xlarge, large, medium)

**Music:**
- Duration (short, medium, long)
- Genre (if available)

**SFX:**
- Duration (quick <2s, medium 2-5s, long >5s)
- Category (if available)

---

## 📱 UI/UX Features

### Responsive Filter Layout
- Filters wrap gracefully on smaller screens
- Touch-friendly button sizes
- Accessible labels and descriptions

### Visual Feedback
- Active filters highlighted with accent color
- Smooth transitions and animations
- Hover states for all interactive elements

### Accessibility
- ARIA labels on remove buttons
- Keyboard navigation support
- Screen reader friendly

---

## 🔧 Technical Implementation

### State Management
```typescript
// Filter metadata from backend
const [availableFilters, setAvailableFilters] = useState<FilterMetadata[]>([]);

// Currently applied filters
const [activeFilters, setActiveFilters] = useState<Record<string, string>>({});
```

### Filter Types
```typescript
interface FilterOption {
  value: string;
  label: string;
  description?: string;
}

interface FilterMetadata {
  name: string;        // e.g., "aspect_ratio"
  label: string;       // e.g., "Aspect Ratio"
  type: string;        // "buttons" | "select"
  options: FilterOption[];
}
```

### Client-Side Filtering Logic
```typescript
const filteredResults = useMemo(() => {
  return results.filter(item => {
    for (const [filterName, filterValue] of Object.entries(activeFilters)) {
      if (filterValue === "all" || !filterValue) continue;
      
      const itemValue = (item as any)[filterName];
      if (itemValue !== filterValue) {
        return false;
      }
    }
    return true;
  });
}, [results, activeFilters]);
```

---

## 🎨 CSS Classes

### Filter Components
- `.filter` - Filter container
- `.filter-label` - Filter label text
- `.filter-pill-group` - Button group container
- `.filter-pill` - Individual filter button
- `.filter-pill.active` - Active filter button
- `.provider-select` - Dropdown select

### Active Filters
- `.active-filters` - Chips container
- `.active-filters-label` - "Active filters:" label
- `.filter-chips` - Chips wrapper
- `.filter-chip` - Individual chip
- `.filter-chip-label` - Chip text
- `.filter-chip-remove` - Remove button (×)
- `.clear-all-filters` - Clear all button

### Results Info
- `.results-info` - Info container
- `.results-count` - Count text

---

## 🚀 Usage Flow

1. **User selects asset type** (e.g., "Videos")
2. **Frontend fetches filters** from `/filters/video`
3. **Filters render dynamically** based on response
4. **User applies filters** (e.g., aspect ratio: 16:9)
5. **Results filter instantly** without API call
6. **Active chips appear** showing applied filters
7. **User can remove filters** individually or clear all

---

## 📊 Performance Optimizations

✅ **useMemo** - Prevents unnecessary re-filtering  
✅ **Client-side filtering** - No API calls for filter changes  
✅ **Lazy loading** - Filters only fetched when needed  
✅ **Debouncing** - Could be added for text input filters  

---

## 🔜 Future Enhancements

- [ ] Multi-select filters (e.g., multiple aspect ratios)
- [ ] Range filters (e.g., duration slider)
- [ ] Color picker for photo color filter
- [ ] Save filter presets
- [ ] URL parameters for shareable filtered searches
- [ ] Filter combinations (AND/OR logic)

---

## 🧪 Testing

To test the dynamic filters:

```bash
# Backend should return filter metadata
curl "http://localhost:8000/filters/video"

# Response should include available filters
{
  "asset_type": "video",
  "filters": [...]
}
```

Then in the UI:
1. Select "Videos" from type filter
2. Filters should appear automatically
3. Apply a filter (e.g., "16:9")
4. See results update instantly
5. Check active filter chips appear
6. Remove filter by clicking ×
7. Verify results update again

---

**All features are live and ready to use!** 🎉
