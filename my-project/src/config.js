// src/config.js
const config = {
  apiBaseUrl: (process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '')
};

export default config;