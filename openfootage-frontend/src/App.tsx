import { useState, useEffect, useMemo } from "react";
import { API_BASE_URL } from "./config";
import "./App.css";

type ProviderFilter = "all" | "pexels" | "pixabay" | "freesound" | "unsplash";
type MediaType = "all" | "video" | "photo" | "vector" | "music" | "sfx" | "illustration";
type SearchMode = "simple" | "smart" | "semantic" | "hybrid";

interface FilterOption {
  value: string;
  label: string;
  description?: string;
}

interface FilterMetadata {
  name: string;
  label: string;
  type: string;
  options: FilterOption[];
}

interface ResultItem {
  id: string;
  provider: string;
  title: string;
  preview_image_url: string;
  page_url: string;
  type: "video" | "photo" | "vector" | "music" | "sfx" | "illustration";
  
  // Video/Photo/Vector specific
  video_url?: string | null;
  width?: number | null;
  height?: number | null;
  
  // Video only
  aspect_ratio?: string | null;
  resolution?: string | null;
  
  // Photo/Vector specific
  orientation?: string | null;
  
  // Audio specific
  audio_url?: string | null;
  duration?: number | null;
  duration_seconds?: number | null;
  tags?: string[];
  
  // Popularity metrics (for music/SFX)
  avg_rating?: number | null;
  num_downloads?: number | null;
  num_ratings?: number | null;
  created?: string | null;
}

const API_URL = API_BASE_URL;
const PER_PAGE = 24;

function App() {
  // Landing page state
  const [showLanding, setShowLanding] = useState(true);
  const [showLegalPage, setShowLegalPage] = useState<string | null>(null);

  // Search state
  const [query, setQuery] = useState("");
  const [provider, setProvider] = useState<ProviderFilter>("all");
  const [mediaType, setMediaType] = useState<MediaType>("video");
  const [mode, setMode] = useState<SearchMode>("simple");

  // Dynamic filters
  // Filters are fetched from backend based on asset type (video, photo, vector, music, sfx)
  // Each asset type has its own relevant filters (e.g., videos have aspect_ratio/resolution,
  // photos have orientation/size/color, music/sfx have duration)
  const [availableFilters, setAvailableFilters] = useState<FilterMetadata[]>([]);
  const [activeFilters, setActiveFilters] = useState<Record<string, string>>({});

  // Data/UI state
  const [results, setResults] = useState<ResultItem[]>([]);
  const [totalHits, setTotalHits] = useState<number | null>(null);
  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'search' | 'network' | 'empty' | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const [activeItem, setActiveItem] = useState<ResultItem | null>(null);

  // Helper to check if item is audio asset
  const isAudioAsset = (item: ResultItem) => {
    return item.type === "music" || item.type === "sfx" || !!item.audio_url;
  };

  // Fetch available filters when media type changes
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const res = await fetch(`${API_URL}/filters/${mediaType}`);
        if (res.ok) {
          const data = await res.json();
          setAvailableFilters(data.filters || []);
        } else {
          // Fallback: Use hardcoded filters if backend endpoint doesn't exist yet
          console.warn(`Backend /filters/${mediaType} not found, using fallback filters`);
          setAvailableFilters(getFallbackFilters(mediaType));
        }
      } catch (err) {
        console.error("Failed to fetch filters:", err);
        // Use fallback on error
        setAvailableFilters(getFallbackFilters(mediaType));
      }
    };
    
    fetchFilters();
    // Clear active filters when media type changes
    setActiveFilters({});
    
    // Reset provider to "all" if current provider doesn't support the new media type
    const supportedProviders: Record<MediaType, ProviderFilter[]> = {
      video: ["all", "pexels", "pixabay"],
      photo: ["all", "pexels", "pixabay", "unsplash"],
      vector: ["all", "pixabay"],
      music: ["all", "freesound"],
      sfx: ["all", "freesound"],
      illustration: ["all", "unsplash"],
      all: ["all", "pexels", "pixabay", "unsplash", "freesound"]
    };
    
    if (!supportedProviders[mediaType].includes(provider)) {
      setProvider("all");
    }
  }, [mediaType, provider]);

  // Fallback filters until backend implements /filters endpoint
  const getFallbackFilters = (type: MediaType): FilterMetadata[] => {
    switch (type) {
      case "video":
        return [
          {
            name: "aspect_ratio",
            label: "Aspect Ratio",
            type: "buttons",
            options: [
              { value: "16:9", label: "16:9" },
              { value: "9:16", label: "9:16" },
              { value: "1:1", label: "1:1" },
              { value: "4:3", label: "4:3" },
              { value: "other", label: "Other" }
            ]
          },
          {
            name: "resolution",
            label: "Resolution",
            type: "buttons",
            options: [
              { value: "SD", label: "SD" },
              { value: "HD", label: "HD" },
              { value: "Full HD", label: "Full HD" },
              { value: "4K", label: "4K" },
              { value: "UHD", label: "UHD (4K+)" }
            ]
          }
        ];
      case "photo":
        return [
          {
            name: "resolution",
            label: "Resolution",
            type: "buttons",
            options: [
              { value: "web", label: "Web (<5MP)" },
              { value: "standard", label: "Standard (5-15MP)" },
              { value: "high", label: "High Res (>15MP)" }
            ]
          },
          {
            name: "orientation",
            label: "Orientation",
            type: "buttons",
            options: [
              { value: "landscape", label: "Landscape" },
              { value: "portrait", label: "Portrait" },
              { value: "square", label: "Square" }
            ]
          }
        ];
      case "vector":
        return [
          {
            name: "orientation",
            label: "Orientation",
            type: "buttons",
            options: [
              { value: "horizontal", label: "Horizontal" },
              { value: "vertical", label: "Vertical" },
              { value: "square", label: "Square" }
            ]
          }
        ];
      case "music":
        return [
          {
            name: "duration",
            label: "Duration",
            type: "buttons",
            options: [
              { value: "short", label: "Short (<30s)" },
              { value: "medium", label: "Medium (30s-1.5min)" },
              { value: "long", label: "Long (>1.5min)" }
            ]
          },
          {
            name: "tag",
            label: "Tag",
            type: "select",
            options: [
              { value: "ambient", label: "Ambient" },
              { value: "chill", label: "Chill" },
              { value: "classical", label: "Classical" },
              { value: "electronic", label: "Electronic" },
              { value: "energetic", label: "Energetic" },
              { value: "jazz", label: "Jazz" },
              { value: "loop", label: "Loop" },
              { value: "piano", label: "Piano" },
              { value: "relaxing", label: "Relaxing" },
              { value: "synth", label: "Synth" }
            ]
          },
          {
            name: "sort",
            label: "Sort By",
            type: "select",
            options: [
              { value: "rating", label: "Highest Rated" },
              { value: "downloads", label: "Most Popular" },
              { value: "created", label: "Newest" }
            ]
          }
        ];
      case "illustration":
        return [
          {
            name: "orientation",
            label: "Orientation",
            type: "buttons",
            options: [
              { value: "landscape", label: "Landscape" },
              { value: "portrait", label: "Portrait" },
              { value: "square", label: "Square" }
            ]
          },
          {
            name: "resolution",
            label: "Resolution",
            type: "buttons",
            options: [
              { value: "web", label: "Web (<5MP)" },
              { value: "standard", label: "Standard (5-15MP)" },
              { value: "high", label: "High Res (>15MP)" }
            ]
          }
        ];
      case "sfx":
        return [
          {
            name: "duration",
            label: "Duration",
            type: "buttons",
            options: [
              { value: "short", label: "Short (<5s)" },
              { value: "medium", label: "Medium (5-15s)" },
              { value: "long", label: "Long (>15s)" }
            ]
          },
          {
            name: "tag",
            label: "Tag",
            type: "select",
            options: [
              { value: "ambience", label: "Ambience" },
              { value: "click", label: "Click" },
              { value: "explosion", label: "Explosion" },
              { value: "foley", label: "Foley" },
              { value: "impact", label: "Impact" },
              { value: "mechanical", label: "Mechanical" },
              { value: "nature", label: "Nature" },
              { value: "voice", label: "Voice" },
              { value: "water", label: "Water" },
              { value: "whoosh", label: "Whoosh" }
            ]
          },
          {
            name: "sort",
            label: "Sort By",
            type: "select",
            options: [
              { value: "rating", label: "Highest Rated" },
              { value: "downloads", label: "Most Popular" },
              { value: "created", label: "Newest" }
            ]
          }
        ];
      default:
        return [];
    }
  };

  // Helper to calculate orientation from width/height
  const getOrientation = (item: ResultItem): string | null => {
    // For photos, always calculate from width/height instead of trusting backend orientation
    if (item.type === "photo" && item.width && item.height) {
      const ratio = item.width / item.height;
      if (Math.abs(ratio - 1) < 0.1) return "square";
      if (ratio > 1) return "landscape";
      return "portrait";
    }
    
    // For other types, use backend orientation if available
    if (item.orientation) return item.orientation;
    if (!item.width || !item.height) return null;
    
    const ratio = item.width / item.height;
    if (Math.abs(ratio - 1) < 0.1) return "square";
    if (ratio > 1) return "landscape";
    return "portrait";
  };

  // Helper to calculate resolution category from width/height (for photos)
  const getResolution = (item: ResultItem): string | null => {
    if (!item.width || !item.height) return null;
    
    const megapixels = (item.width * item.height) / 1_000_000;
    
    if (megapixels < 5) return "web";
    if (megapixels <= 15) return "standard";
    return "high";
  };

  // Helper to normalize resolution/aspect ratio values for comparison
  const normalizeFilterValue = (value: string): string => {
    return value
      .toLowerCase()
      .trim()
      .replace(/\s+/g, ''); // Remove all spaces (e.g., "Full HD" -> "fullhd")
  };

  // Client-side filtered results for instant filtering
  const filteredResults = useMemo(() => {
    // For music/SFX, all filtering is done server-side, so just return all results
    const isMusicOrSfx = mediaType === "music" || mediaType === "sfx";
    if (isMusicOrSfx) {
      return results;
    }
    
    return results.filter(item => {
      // Apply all active filters
      for (const [filterName, filterValue] of Object.entries(activeFilters)) {
        if (filterValue === "all" || !filterValue) continue;
        
        // Skip filters that are handled server-side (this shouldn't happen for video/photo/vector)
        if (filterName === "sort" || filterName === "tag" || filterName === "duration") continue;
        
        // Special handling for orientation filter
        if (filterName === "orientation") {
          const itemOrientation = getOrientation(item);
          if (itemOrientation !== filterValue) {
            return false;
          }
        }
        // Special handling for resolution filter (photos and illustrations)
        else if (filterName === "resolution" && (mediaType === "photo" || mediaType === "illustration")) {
          const itemResolution = getResolution(item);
          if (itemResolution !== filterValue) {
            return false;
          }
        }
        else {
          // Get the item's value for this filter
          let itemValue = (item as any)[filterName];
          
          // Normalize both values for comparison
          if (typeof itemValue === 'string' && typeof filterValue === 'string') {
            const normalizedItemValue = normalizeFilterValue(itemValue);
            const normalizedFilterValue = normalizeFilterValue(filterValue);
            
            if (normalizedItemValue !== normalizedFilterValue) {
              return false;
            }
          } else if (itemValue !== filterValue) {
            return false;
          }
        }
      }
      
      return true;
    });
  }, [results, activeFilters, mediaType]);

  // Get friendly error message based on state
  const getEmptyStateMessage = () => {
    if (error) {
      if (errorType === 'network') {
        return "This provider is temporarily unavailable. Try another source or check back later.";
      }
      return "Something went wrong. Please try again.";
    }
    
    // Only show empty message if a search has been performed
    if (!loading && hasSearched && results.length === 0) {
      return "No results found. Try different keywords or adjust your filters.";
    }
    
    if (!loading && results.length > 0 && filteredResults.length === 0) {
      return "No results match your current filters. Try adjusting them.";
    }
    
    return null;
  };

  // ------------------------------------
  // SEARCH FUNCTION
  // ------------------------------------

  const runSearchWithFilters = async (nextPage = 1, append = false, filters = activeFilters) => {
    // Allow empty query for music/SFX (backend uses smart defaults)
    const isMusicOrSfx = mediaType === "music" || mediaType === "sfx";
    if (!query.trim() && !isMusicOrSfx) return;

    try {
      if (nextPage === 1) setLoading(true);
      else setLoadingMore(true);

      setError(null);

      let endpoint = `/search/${mode}`;

      const params = new URLSearchParams();
      params.set("query", query || "");
      params.set("type", mediaType);
      params.set("page", String(nextPage));
      params.set("per_page", String(PER_PAGE));

      if (provider !== "all") params.set("provider", provider);
      
      // Add backend filters for music/SFX using the provided filters parameter
      if (filters.tag) params.set("tag", filters.tag);
      if (filters.sort) params.set("sort", filters.sort);
      if (filters.duration && isMusicOrSfx) params.set("duration", filters.duration);
      
      // Note: aspect_ratio, resolution, orientation are filtered client-side for instant filtering

      const requestUrl = `${API_URL}${endpoint}?${params.toString()}`;
      console.log("Search request:", requestUrl);
      
      const res = await fetch(requestUrl);
      if (!res.ok) {
        const errorText = await res.text();
        console.error("API error response:", res.status, errorText);
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      
      // Debug: log the response to check data structure
      console.log("API Response:", data);
      console.log("Results count:", data.results?.length || 0);
      console.log("First result:", data.results?.[0]);
      
      // Debug: Check what resolution/aspect_ratio values we're getting
      if (data.results && data.results.length > 0) {
        const uniqueResolutions = [...new Set(data.results.map((r: any) => r.resolution).filter(Boolean))];
        const uniqueAspectRatios = [...new Set(data.results.map((r: any) => r.aspect_ratio).filter(Boolean))];
        console.log("Available resolutions:", uniqueResolutions);
        console.log("Available aspect ratios:", uniqueAspectRatios);
      }

      const incoming = data.results || [];
      setTotalHits(data.estimatedTotalHits || 0);

      if (append) setResults((old) => [...old, ...incoming]);
      else setResults(incoming);

      setPage(nextPage);
      setHasSearched(true);
    } catch (err: any) {
      console.error(err);
      const isNetworkError = err.message?.includes('Failed to fetch') || err.message?.includes('Network');
      setError(err.message || "Search failed.");
      setErrorType(isNetworkError ? 'network' : 'search');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // Wrapper function that uses current activeFilters state
  const runSearch = async (nextPage = 1, append = false) => {
    return runSearchWithFilters(nextPage, append, activeFilters);
  };

  // ------------------------------------
  // HANDLERS
  // ------------------------------------

  const startSearch = () => {
    const isMusicOrSfx = mediaType === "music" || mediaType === "sfx";
    
    // Music/SFX can browse without query (backend uses smart defaults)
    // Other types require query text
    if (query.trim() || isMusicOrSfx) {
      setError(null);
      setErrorType(null);
      runSearch(1, false);
    }
  };

  const loadMore = () => {
    if (!loading && !loadingMore && results.length < (totalHits || 0)) {
      runSearch(page + 1, true);
    }
  };

  const handleFilterChange = (filterName: string, value: string) => {
    const newFilters = {
      ...activeFilters,
      [filterName]: value
    };
    
    setActiveFilters(newFilters);
    
    // If changing server-side filters, trigger new search immediately
    // Only auto-trigger if user has already performed a search (results exist)
    const isMusicOrSfx = mediaType === "music" || mediaType === "sfx";
    const isServerSideFilter = filterName === "tag" || filterName === "sort" || 
                               (filterName === "duration" && isMusicOrSfx);
    
    if (isServerSideFilter && hasSearched) {
      // Trigger search with the updated filters
      runSearchWithFilters(1, false, newFilters);
    }
  };

  const removeFilter = (filterName: string) => {
    setActiveFilters(prev => {
      const newFilters = { ...prev };
      delete newFilters[filterName];
      return newFilters;
    });
  };

  const clearAllFilters = () => {
    setActiveFilters({});
  };

  // ------------------------------------
  // RENDER
  // ------------------------------------

  if (showLanding) {
    return (
      <div className="landing-container">
        {/* HERO SECTION */}
        <section className="hero-section">
          <div className="hero-bg-typography">
            <span className="hero-bg-text hero-bg-1">VIDEO</span>
            <span className="hero-bg-text hero-bg-2">PHOTOS</span>
            <span className="hero-bg-text hero-bg-3">MUSIC</span>
            <span className="hero-bg-text hero-bg-4">VECTORS</span>
            <span className="hero-bg-text hero-bg-5">SFX</span>
          </div>
          <div className="hero-content">
            <div className="hero-logo-group">
              <div className="hero-logo-mark">▶</div>
              <div>
                <div className="hero-logo-text">OpenFootage <span className="beta-badge">beta</span></div>
              </div>
            </div>
            <h1 className="hero-headline">
              One Search Bar.<br />
              All Your Stock Media.
            </h1>
            <p className="hero-subheadline">
              All your stock sources in one place, so you can move fast and make better creative projects.
            </p>
            <button className="hero-cta" onClick={() => setShowLanding(false)}>
              Search Everything →
            </button>
            <p className="hero-tagline">
              One search. Multiple providers. Zero friction.
            </p>
          </div>
        </section>

        {/* WHAT WE OFFER */}
        <section className="features-section">
          <h2 className="features-title">Why You'll Love This</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3 className="feature-title">Unified Search</h3>
              <p className="feature-text">
                Pexels, Pixabay, Unsplash, Freesound: all under one search bar.
              </p>
            </div>
            <div className="feature-card">
              <h3 className="feature-title">All Media, One Flow</h3>
              <p className="feature-text">
                Clips, images, audio, graphics... whatever your project needs.
              </p>
            </div>
            <div className="feature-card">
              <h3 className="feature-title">Built for Fast Creators</h3>
              <p className="feature-text">
                Filters that actually help. A layout that doesn't fight you.
              </p>
            </div>
          </div>
        </section>

        {/* CTA SECTION */}
        <section className="cta-section">
          <h2 className="cta-headline">Speed Up Your Creative Process</h2>
          <p className="cta-text">
            Get the assets you need in seconds, not hours.
          </p>
          <button className="cta-button" onClick={() => setShowLanding(false)}>
            OpenFootage →
          </button>
        </section>

        {/* FOOTER */}
        <footer className="app-footer">
          <div className="footer-content">
            <span>© 2025 OpenFootage — Demo Version</span>
            <div className="footer-links">
              <button onClick={() => setShowLegalPage('terms')} className="footer-link">Terms</button>
              <button onClick={() => setShowLegalPage('privacy')} className="footer-link">Privacy</button>
              <button onClick={() => setShowLegalPage('dmca')} className="footer-link">DMCA</button>
              <button onClick={() => setShowLegalPage('attribution')} className="footer-link">Attribution</button>
            </div>
          </div>
        </footer>
      </div>
    );
  }

  return (
    <div className="app-container">

      {/* TOP HEADER / LOGO BAR */}
      <div className="app-header">
        <div className="logo-group">
          <div className="logo-mark">▶</div>
          <div>
            <div className="logo-text-main">openfootage <span className="beta-badge">beta</span></div>
            <div className="logo-text-sub">media search</div>
          </div>
        </div>
      </div>

      {/* SEARCH BAR */}
      <div className="search-card">
        <input
          className="search-input"
          placeholder={
            mediaType === "music" || mediaType === "sfx"
              ? "Search or browse by filters..."
              : "Search footage..."
          }
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && startSearch()}
        />

        <button className="search-btn" onClick={startSearch} disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* FILTERS */}
      <div className="filters-row">

        {/* Media Type - 5 buttons */}
        <div className="filter">
          <span className="filter-label">Type</span>
          <div className="filter-pill-group">
            {[
              { value: "video", label: "Videos", icon: "🎥" },
              { value: "photo", label: "Photos", icon: "📷" },
              { value: "illustration", label: "Illustrations", icon: "🖼️" },
              { value: "vector", label: "Vectors", icon: "🎨" },
              { value: "music", label: "Music", icon: "🎵" },
              { value: "sfx", label: "SFX", icon: "🔊" }
            ].map((type) => (
              <button
                key={type.value}
                className={mediaType === type.value ? "filter-pill active" : "filter-pill"}
                onClick={() => setMediaType(type.value as MediaType)}
              >
                <span style={{ marginRight: '4px' }}>{type.icon}</span>
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Provider */}
        <div className="filter">
          <span className="filter-label">Provider</span>
          <select
            className="provider-select"
            value={provider}
            onChange={(e) => setProvider(e.target.value as ProviderFilter)}
          >
            <option value="all">All</option>
            {(mediaType === "video" || mediaType === "photo" || mediaType === "all") && <option value="pexels">Pexels</option>}
            {(mediaType === "video" || mediaType === "photo" || mediaType === "vector" || mediaType === "all") && <option value="pixabay">Pixabay</option>}
            {(mediaType === "photo" || mediaType === "illustration" || mediaType === "all") && <option value="unsplash">Unsplash</option>}
            {(mediaType === "music" || mediaType === "sfx" || mediaType === "all") && <option value="freesound">Freesound</option>}
          </select>
        </div>

        {/* Mode */}
        <div className="filter">
          <span className="filter-label">Mode</span>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as SearchMode)}
            className="provider-select"
          >
            <option value="simple">Simple</option>
            <option value="smart">Smart</option>
            <option value="semantic">Semantic</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>
      </div>

      {/* Dynamic Filters Row - Appears below main filters */}
      {availableFilters.length > 0 && (
        <div className="filters-row secondary-filters">
          {availableFilters.map((filter) => (
            <div key={filter.name} className="filter">
              <span className="filter-label">{filter.label}</span>
              {filter.type === "select" && (
                <select
                  className="provider-select"
                  value={activeFilters[filter.name] || "all"}
                  onChange={(e) => handleFilterChange(filter.name, e.target.value)}
                >
                  <option value="all">All</option>
                  {filter.options.map((opt) => (
                    <option key={opt.value} value={opt.value} title={opt.description}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              )}
              {filter.type === "buttons" && (
                <div className="filter-pill-group">
                  <button
                    className={(!activeFilters[filter.name] || activeFilters[filter.name] === "all") ? "filter-pill active" : "filter-pill"}
                    onClick={() => handleFilterChange(filter.name, "all")}
                  >
                    All
                  </button>
                  {filter.options.map((opt) => (
                    <button
                      key={opt.value}
                      className={activeFilters[filter.name] === opt.value ? "filter-pill active" : "filter-pill"}
                      onClick={() => handleFilterChange(filter.name, opt.value)}
                      title={opt.description}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Active Filter Chips */}
      {Object.keys(activeFilters).length > 0 && (
        <div className="active-filters">
          <span className="active-filters-label">Active filters:</span>
          <div className="filter-chips">
            {Object.entries(activeFilters).map(([filterName, filterValue]) => {
              if (filterValue === "all" || !filterValue) return null;
              
              // Find the filter metadata to get the label
              const filterMeta = availableFilters.find(f => f.name === filterName);
              const optionMeta = filterMeta?.options.find(o => o.value === filterValue);
              
              return (
                <div key={filterName} className="filter-chip">
                  <span className="filter-chip-label">
                    {filterMeta?.label || filterName}: {optionMeta?.label || filterValue}
                  </span>
                  <button
                    className="filter-chip-remove"
                    onClick={() => removeFilter(filterName)}
                    aria-label={`Remove ${filterName} filter`}
                  >
                    ×
                  </button>
                </div>
              );
            })}
            {Object.keys(activeFilters).length > 1 && (
              <button className="clear-all-filters" onClick={clearAllFilters}>
                Clear all
              </button>
            )}
          </div>
        </div>
      )}

      {/* RESULTS */}
      {getEmptyStateMessage() && (
        <div className="empty-state">
          <div className="empty-state-icon">
            {error ? '⚠️' : '🔍'}
          </div>
          <div className="empty-state-message">{getEmptyStateMessage()}</div>
        </div>
      )}

      {results.length > 0 && (
        <div className="results-info">
          <span className="results-count">
            Showing {filteredResults.length} of {results.length} results
            {totalHits && totalHits > results.length && ` (${totalHits.toLocaleString()} total available)`}
          </span>
        </div>
      )}

      <div className="results-grid">
        {filteredResults.map((item, index) => {
          const isAudio = isAudioAsset(item);
          return (
            <div
              key={`${item.id}-${index}`}
              className={`result-item ${isAudio ? 'audio-card' : ''}`}
              onClick={() => setActiveItem(item)}
            >
              {isAudio ? (
                <div className="audio-preview">
                  {item.preview_image_url ? (
                    <img src={item.preview_image_url} alt={item.title} className="waveform-img" />
                  ) : (
                    <div className="audio-icon">{item.type === 'music' ? '🎵' : '🔊'}</div>
                  )}
                  <div className="audio-title">{item.title}</div>
                  {item.duration && (
                    <div className="audio-duration">
                      {item.duration < 60 ? `${item.duration}s` : `${Math.floor(item.duration / 60)}:${String(item.duration % 60).padStart(2, '0')}`}
                    </div>
                  )}
                  {!item.audio_url && (
                    <div className="audio-unavailable">Preview unavailable</div>
                  )}
                </div>
              ) : (
                <>
                  <img src={item.preview_image_url} alt={item.title} />
                  <div className="thumbnail-badges">
                    {item.type === 'vector' && (
                      <div className="badge vector-badge">Vector</div>
                    )}
                    {item.type === 'video' && item.aspect_ratio && (
                      <div className="badge aspect-badge">{item.aspect_ratio}</div>
                    )}
                    {item.type === 'video' && item.resolution && (
                      <div className="badge resolution-badge">{item.resolution.toUpperCase()}</div>
                    )}
                  </div>
                </>
              )}
              <div className="result-provider">{item.provider}</div>
            </div>
          );
        })}
      </div>

      {/* Load More */}
      {results.length < (totalHits || 0) && (
        <div className="load-more-container">
          <button
            className="load-more-btn"
            onClick={loadMore}
            disabled={loadingMore}
          >
            {loadingMore ? "Loading..." : "Load More"}
          </button>
        </div>
      )}

      {/* PREVIEW MODAL */}
      {activeItem && (
        <div className="modal-overlay" onClick={() => setActiveItem(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            {activeItem.audio_url ? (
              <div className="audio-modal">
                {activeItem.preview_image_url ? (
                  <img src={activeItem.preview_image_url} alt={activeItem.title} className="waveform-modal" />
                ) : (
                  <div className="audio-icon-large">{activeItem.type === 'music' ? '🎵' : '🔊'}</div>
                )}
                <audio controls src={activeItem.audio_url} className="modal-audio">
                  Your browser does not support the audio element.
                </audio>
                {activeItem.duration && (
                  <div className="audio-info">Duration: {activeItem.duration < 60 ? `${activeItem.duration}s` : `${Math.floor(activeItem.duration / 60)}:${String(activeItem.duration % 60).padStart(2, '0')}`}</div>
                )}
              </div>
            ) : (activeItem.type === 'music' || activeItem.type === 'sfx') ? (
              <div className="audio-modal">
                {activeItem.preview_image_url ? (
                  <img src={activeItem.preview_image_url} alt={activeItem.title} className="waveform-modal" />
                ) : (
                  <div className="audio-icon-large">{activeItem.type === 'music' ? '🎵' : '🔊'}</div>
                )}
                <div className="audio-unavailable-modal">Audio preview not available</div>
              </div>
            ) : activeItem.video_url ? (
              <video controls src={activeItem.video_url} className="modal-video" />
            ) : (
              <img
                className={`modal-img ${activeItem.type === 'vector' ? 'modal-img-vector' : 'modal-img-photo'}`}
                src={activeItem.preview_image_url}
                alt={activeItem.title}
              />
            )}

            <div className="modal-title">{activeItem.title}</div>
            <div className="modal-badges">
              {activeItem.aspect_ratio && (
                <span className="modal-badge">
                  <span className="badge-icon">📐</span> {activeItem.aspect_ratio}
                </span>
              )}
              {activeItem.resolution && (
                <span className="modal-badge">
                  <span className="badge-icon">🎬</span> {activeItem.resolution.toUpperCase()}
                </span>
              )}
            </div>
            <a href={activeItem.page_url} target="_blank" className="modal-link">
              Open on provider site →
            </a>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="app-footer">
        <div className="footer-content">
          <span>© 2025 OpenFootage — Demo Version</span>
          <div className="footer-links">
            <button onClick={() => setShowLegalPage('terms')} className="footer-link">Terms</button>
            <button onClick={() => setShowLegalPage('privacy')} className="footer-link">Privacy</button>
            <button onClick={() => setShowLegalPage('dmca')} className="footer-link">DMCA</button>
            <button onClick={() => setShowLegalPage('attribution')} className="footer-link">Attribution</button>
          </div>
        </div>
      </footer>

      {/* LEGAL PAGE MODAL */}
      {showLegalPage && (
        <div className="legal-modal-overlay" onClick={() => setShowLegalPage(null)}>
          <div className="legal-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="legal-modal-close" onClick={() => setShowLegalPage(null)}>×</button>
            <div className="legal-modal-body">
              {showLegalPage === 'terms' && (
                <div className="legal-page">
                  <h1>Terms of Use</h1>
                  <p className="legal-date">Last Updated: December 13, 2025</p>

                  <section className="legal-section">
                    <h2>1. Nature of Service</h2>
                    <p>
                      OpenFootage is a <strong>demo application</strong> designed to showcase unified search capabilities 
                      across multiple stock media providers. This is not a production service and should not be relied 
                      upon for commercial or critical purposes.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>2. Third-Party Content</h2>
                    <p>
                      All media content displayed through OpenFootage is sourced from third-party providers including 
                      Pexels, Pixabay, Unsplash, and Freesound. We do not host, own, or claim any rights to this content.
                    </p>
                    <p>
                      Each provider has its own terms of service and licensing requirements. When you download or use 
                      any media from these providers, you are subject to their respective terms.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>3. Demo Limitations</h2>
                    <p>As a demonstration project:</p>
                    <ul>
                      <li>Service availability is not guaranteed</li>
                      <li>Search results may be incomplete or inaccurate</li>
                      <li>Features may change or be removed without notice</li>
                      <li>No data persistence or user accounts are provided</li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>4. Acceptable Use</h2>
                    <p>Users of this demo agree to:</p>
                    <ul>
                      <li>Not attempt to circumvent rate limits or API restrictions</li>
                      <li>Not scrape or systematically download content</li>
                      <li>Respect the terms of service of all third-party providers</li>
                      <li>Use the service for evaluation and testing purposes only</li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>5. Intellectual Property</h2>
                    <p>
                      The OpenFootage application code and interface design are provided as-is for demonstration purposes. 
                      All media content remains the property of respective copyright holders and providers.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>6. Copyright and DMCA</h2>
                    <p>
                      If you believe content displayed through OpenFootage infringes your copyright, please contact 
                      the original content provider directly. OpenFootage does not host any media files.
                    </p>
                    <p>
                      For concerns about the OpenFootage application itself, see our <button onClick={() => setShowLegalPage('dmca')} className="inline-link">DMCA Policy</button>.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>7. Disclaimers and Limitation of Liability</h2>
                    <p>
                      OpenFootage is provided "AS IS" without warranties of any kind. We make no guarantees about 
                      service availability, accuracy, or fitness for any particular purpose.
                    </p>
                    <p>
                      The creators and operators of OpenFootage shall not be liable for any damages arising from 
                      the use or inability to use this demo application.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>8. Changes to Terms</h2>
                    <p>
                      These terms may be updated at any time. Continued use of OpenFootage constitutes acceptance 
                      of any changes.
                    </p>
                  </section>
                </div>
              )}
              {showLegalPage === 'privacy' && (
                <div className="legal-page">
                  <h1>Privacy Policy</h1>
                  <p className="legal-date">Last Updated: December 13, 2025</p>

                  <section className="legal-section">
                    <h2>1. Information We Collect</h2>
                    <p>
                      OpenFootage is a demo application that operates without user accounts or persistent data storage. 
                      We collect minimal information necessary for the application to function:
                    </p>
                    <ul>
                      <li><strong>Search Queries:</strong> Temporarily processed to fetch results from third-party APIs</li>
                      <li><strong>Technical Data:</strong> Standard server logs including IP addresses, browser type, and timestamps</li>
                      <li><strong>Usage Analytics:</strong> Anonymous aggregated data about feature usage and performance</li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>2. How We Use Your Information</h2>
                    <p>The limited data we collect is used solely to:</p>
                    <ul>
                      <li>Process search requests and display results</li>
                      <li>Maintain and improve application functionality</li>
                      <li>Debug technical issues</li>
                      <li>Understand usage patterns for development purposes</li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>3. Third-Party Services</h2>
                    <p>
                      OpenFootage integrates with external APIs from Pexels, Pixabay, Unsplash, and Freesound. 
                      When you perform a search, your query is transmitted to these services according to their 
                      respective privacy policies:
                    </p>
                    <ul>
                      <li><a href="https://www.pexels.com/privacy-policy/" target="_blank" rel="noopener noreferrer">Pexels Privacy Policy</a></li>
                      <li><a href="https://pixabay.com/service/privacy/" target="_blank" rel="noopener noreferrer">Pixabay Privacy Policy</a></li>
                      <li><a href="https://unsplash.com/privacy" target="_blank" rel="noopener noreferrer">Unsplash Privacy Policy</a></li>
                      <li><a href="https://freesound.org/help/privacy/" target="_blank" rel="noopener noreferrer">Freesound Privacy Policy</a></li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>4. Data Storage and Retention</h2>
                    <p>
                      As a demo application, OpenFootage does not maintain user accounts or persistent user data. 
                      Search queries are processed in real-time and not permanently stored. Server logs are 
                      retained temporarily for debugging purposes only.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>5. Cookies and Local Storage</h2>
                    <p>
                      OpenFootage may use browser local storage to remember your preferences (such as selected 
                      media type or search mode) during your session. This data remains on your device and is 
                      not transmitted to our servers.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>6. Your Rights</h2>
                    <p>
                      Since we do not collect or store personal information beyond temporary server logs, 
                      there is no persistent data to access, modify, or delete. If you have concerns about 
                      data collected by third-party providers, please contact them directly.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>7. Changes to This Policy</h2>
                    <p>
                      This privacy policy may be updated as the demo evolves. Any changes will be reflected 
                      on this page with an updated date.
                    </p>
                  </section>
                </div>
              )}
              {showLegalPage === 'dmca' && (
                <div className="legal-page">
                  <h1>DMCA Copyright Policy</h1>
                  <p className="legal-date">Last Updated: December 13, 2025</p>

                  <section className="legal-section">
                    <h2>Important Notice</h2>
                    <p>
                      OpenFootage is a <strong>search aggregator and demo application</strong>. We do not host, 
                      store, or serve any media files (videos, photos, audio, or vectors). All content displayed 
                      through OpenFootage is hosted by and remains under the control of third-party providers.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>Content Providers</h2>
                    <p>Media content shown in search results comes from:</p>
                    <ul>
                      <li><strong>Pexels:</strong> <a href="https://www.pexels.com" target="_blank" rel="noopener noreferrer">https://www.pexels.com</a></li>
                      <li><strong>Pixabay:</strong> <a href="https://pixabay.com" target="_blank" rel="noopener noreferrer">https://pixabay.com</a></li>
                      <li><strong>Unsplash:</strong> <a href="https://unsplash.com" target="_blank" rel="noopener noreferrer">https://unsplash.com</a></li>
                      <li><strong>Freesound:</strong> <a href="https://freesound.org" target="_blank" rel="noopener noreferrer">https://freesound.org</a></li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>Copyright Complaints</h2>
                    <p>
                      If you believe your copyrighted work is being displayed through OpenFootage without authorization:
                    </p>
                    <ol>
                      <li>
                        <strong>Contact the source provider directly:</strong> Since we don't host content, 
                        copyright takedown requests must be directed to the provider hosting the material.
                      </li>
                      <li>
                        <strong>For concerns about OpenFootage itself:</strong> If you believe the OpenFootage 
                        application or its source code infringes your rights, contact us with details.
                      </li>
                    </ol>
                  </section>

                  <section className="legal-section">
                    <h2>DMCA Takedown Requests</h2>
                    <p>A valid DMCA notice should include:</p>
                    <ul>
                      <li>Your contact information (name, address, phone, email)</li>
                      <li>Identification of the copyrighted work claimed to be infringed</li>
                      <li>Identification of the infringing material and its location</li>
                      <li>A statement of good faith belief that use is not authorized</li>
                      <li>A statement that the information is accurate and you are authorized to act</li>
                      <li>Your physical or electronic signature</li>
                    </ul>
                  </section>

                  <section className="legal-section">
                    <h2>Contact Information</h2>
                    <p className="contact-email">dmca@openfootage.demo</p>
                    <p className="legal-note">
                      Note: This is a demo application. The above email is illustrative. In a production 
                      environment, valid contact details would be provided.
                    </p>
                  </section>
                </div>
              )}
              {showLegalPage === 'attribution' && (
                <div className="legal-page">
                  <h1>Attribution & Source Providers</h1>
                  <p className="legal-date">Last Updated: December 13, 2025</p>

                  <section className="legal-section">
                    <p>
                      OpenFootage aggregates search results from the following free stock media providers. 
                      All content displayed belongs to these platforms and their respective contributors.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>Content Providers</h2>
                    
                    <div className="provider-attribution">
                      <h3>Unsplash</h3>
                      <p>
                        Beautiful, free photos contributed by talented photographers worldwide.
                      </p>
                      <ul className="provider-links">
                        <li><a href="https://unsplash.com" target="_blank" rel="noopener noreferrer">Website: unsplash.com</a></li>
                        <li><a href="https://unsplash.com/license" target="_blank" rel="noopener noreferrer">License Information</a></li>
                      </ul>
                    </div>

                    <div className="provider-attribution">
                      <h3>Pexels</h3>
                      <p>
                        Free stock photos and videos shared by creators everywhere.
                      </p>
                      <ul className="provider-links">
                        <li><a href="https://www.pexels.com" target="_blank" rel="noopener noreferrer">Website: pexels.com</a></li>
                        <li><a href="https://www.pexels.com/license/" target="_blank" rel="noopener noreferrer">License Information</a></li>
                      </ul>
                    </div>

                    <div className="provider-attribution">
                      <h3>Pixabay</h3>
                      <p>
                        Stunning free images, videos, and music shared by a vibrant community.
                      </p>
                      <ul className="provider-links">
                        <li><a href="https://pixabay.com" target="_blank" rel="noopener noreferrer">Website: pixabay.com</a></li>
                        <li><a href="https://pixabay.com/service/license/" target="_blank" rel="noopener noreferrer">License Information</a></li>
                      </ul>
                    </div>

                    <div className="provider-attribution">
                      <h3>Freesound</h3>
                      <p>
                        A collaborative database of Creative Commons licensed sounds.
                      </p>
                      <ul className="provider-links">
                        <li><a href="https://freesound.org" target="_blank" rel="noopener noreferrer">Website: freesound.org</a></li>
                        <li><a href="https://freesound.org/help/faq/#licenses" target="_blank" rel="noopener noreferrer">License Information</a></li>
                      </ul>
                    </div>
                  </section>

                  <section className="legal-section">
                    <h2>Usage and Licensing</h2>
                    <p>
                      Each provider has its own licensing terms. While most content is free to use, 
                      some may require attribution or have specific usage restrictions. Always check 
                      the license for each individual asset before using it in your projects.
                    </p>
                  </section>

                  <section className="legal-section">
                    <h2>Acknowledgments</h2>
                    <p>
                      OpenFootage is built with gratitude for these platforms and their communities 
                      of creators who make high-quality media accessible to everyone.
                    </p>
                  </section>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
