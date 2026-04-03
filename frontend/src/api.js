import axios from 'axios';

const api = axios.create({
  baseURL: 'https://vintage-backend-tk3c.onrender.com/api',
});

export default api;
