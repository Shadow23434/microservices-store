import axiosClient from './axiosClient';

const customerService = {
  // Lấy danh sách khách hàng
  getCustomers: () => axiosClient.get('/api/customers/'),
  // Lấy thông tin 1 khách hàng
  getCustomer: (id: number) => axiosClient.get(`/api/customers/${id}/`),
  // Tạo tài khoản khách hàng mới (đăng ký)
  // data: { name, email, phone, address, ... }
  createCustomer: (data: any) => axiosClient.post('/api/customers/', data),
  // Cập nhật thông tin khách hàng (full update)
  updateCustomer: (id: number, data: any) =>
    axiosClient.put(`/api/customers/${id}/`, data),
  // Cập nhật 1 phần thông tin khách hàng
  patchCustomer: (id: number, data: any) =>
    axiosClient.patch(`/api/customers/${id}/`, data),
  // Xóa tài khoản khách hàng
  deleteCustomer: (id: number) => axiosClient.delete(`/api/customers/${id}/`),
};

export default customerService;
