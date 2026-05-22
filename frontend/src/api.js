import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

// Normalize backend 422 payload into a flat string the UI can display.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.errors) {
      const lines = error.response.data.errors
        .map((e) => `${e.field}: ${e.message}`)
        .join('\n');
      error.friendlyMessage = `${error.response.data.detail}\n${lines}`;
    } else if (error.response?.data?.detail) {
      error.friendlyMessage = error.response.data.detail;
    } else {
      error.friendlyMessage = error.message || 'Network error';
    }
    return Promise.reject(error);
  }
);

export default api;
