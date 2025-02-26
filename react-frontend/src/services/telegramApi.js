import axios from 'axios';

const telegramApi = axios.create({
  baseURL: process.env.REACT_APP_TELEGRAM_API_URL || 'http://localhost:8001',
  timeout: 10000,
});

export default telegramApi;