import axios from 'axios';
import Cookies from 'js-cookie';

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
  withCredentials: true,
});

axiosInstance.interceptors.request.use(
  (config) => {
    const safeMethods = ['get', 'head', 'options'];
    if (config.method && !safeMethods.includes(config.method.toLowerCase())) {
      // Flask-WTF default header name is 'X-CSRF-Token'.
      // The backend sends the cookie with the key 'csrf_token'.
      const token = Cookies.get('csrf_token');
      if (token) {
        config.headers['X-CSRF-Token'] = token;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;