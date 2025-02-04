const BASE_URL = import.meta.env.DEV
  ? "http://127.0.0.1:8000" // Development URL
  : ""; // Production URL

export const API_BASE_URL = BASE_URL; // Replace with your FastAPI server URL
