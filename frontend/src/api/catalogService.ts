import axiosClient from './axiosClient';

const catalogService = {
  // Lấy toàn bộ danh mục
  getCategories: () => axiosClient.get('/api/categories/'),
  // Lấy chi tiết 1 danh mục
  getCategoryById: (id: number) => axiosClient.get(`/api/categories/${id}/`),
  // Tạo danh mục mới (admin)
  createCategory: (data: any) => axiosClient.post('/api/categories/', data),
  // Cập nhật danh mục (admin)
  updateCategory: (id: number, data: any) => axiosClient.put(`/api/categories/${id}/`, data),
  // Xóa danh mục (admin)
  deleteCategory: (id: number) => axiosClient.delete(`/api/categories/${id}/`),
};

export default catalogService;
