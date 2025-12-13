// src/config.ts

// This should point to your running FastAPI backend.
// You can override this by creating a .env file with:
// VITE_API_URL=http://localhost:8000 (for local backend)
// or leave it empty to use Railway in development

const envApiUrl = import.meta.env.VITE_API_URL;

// If VITE_API_URL is explicitly set, use it
// Otherwise, use Railway backend as default
export const API_BASE_URL = envApiUrl || 'https://openfootage-production.up.railway.app';