// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://fastapi:1236',
  timeout: 10000000,
});

// Add a response interceptor for handling token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401 && localStorage.getItem('token')) {
      // Clear token and redirect to login if token is expired
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;