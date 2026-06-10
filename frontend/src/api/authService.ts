import axiosClient from './axiosClient';

// Auth dùng customer-service:
// POST /api/customers/          → Tạo tài khoản (đăng ký)
// GET  /api/customers/          → Tìm customer theo email
// GET  /api/customers/{id}/     → Lấy profile
// PUT  /api/customers/{id}/     → Cập nhật profile

const authService = {
  // Đăng ký tài khoản mới (tạo customer)
  register: (data: any) => axiosClient.post('/api/customers/', data),
  // Lấy danh sách customer $ể tìm theo email (không có endpoint login thật)
  getCustomers: () => axiosClient.get('/api/customers/'),
  // Lấy thông tin profile của customer
  getProfile: (id: number) => axiosClient.get(`/api/customers/${id}/`),
  // Cập nhật thông tin profile
  updateProfile: (id: number, data: any) => axiosClient.put(`/api/customers/${id}/`, data),
};

export default authService;
