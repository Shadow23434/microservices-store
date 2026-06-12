/// <reference types="vite/client" />
import axios from 'axios';

// Tự động detect môi trường:
// - Production (deployed): dùng relative path (Vercel rewrite hoặc same-origin)
// - Development: dùng localhost:8888 (API Gateway local)
const isProduction = import.meta.env.PROD;
const defaultBaseURL = isProduction ? '' : 'http://localhost:8888';

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || defaultBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor cho Request: Tự $ộng $ính kèm Token
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor cho Response: Xử lý lỗi chung (VD: Hết hạn token)
axiosClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Xử lý refresh token hoặc $á user ra trang Login
      console.log('Token hết hạn, vui lòng $ăng nhập lại');
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
