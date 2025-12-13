// src/config.ts

// This should point to your running FastAPI backend.
// For mobile testing, it uses the current hostname instead of localhost
const isLocalhost = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1' || 
                    window.location.hostname === '';

export const API_BASE_URL = isLocalhost 
  ? "http://localhost:8000"
  : `http://${window.location.hostname}:8000`;