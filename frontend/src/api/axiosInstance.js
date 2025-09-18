// =================================================================
// FILE: frontend/src/api/axiosInstance.js
// =================================================================
import axios from 'axios';

// Create a new axios instance
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
  withCredentials: true,
});

// Add a request interceptor to attach the CSRF token
// We will get the token from a simple cookie storage, which will be set by our AuthProvider
axiosInstance.interceptors.request.use(config => {
  // Flask-WTF default cookie name is 'csrf_token' and header name is 'X-CSRFToken'
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  if (config.method !== 'get' && config.method !== 'head' && config.method !== 'options') {
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }
  return config;
}, error => {
  return Promise.reject(error);
});


export default axiosInstance;