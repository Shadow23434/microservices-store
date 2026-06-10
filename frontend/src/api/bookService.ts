import axiosClient from './axiosClient';

const bookService = {
  // Lấy danh sách tất cả sách, có thể filter hoặc search theo params
  getAllBooks: (params?: any) => axiosClient.get('/api/books/', { params }),
  // Lấy chi tiết 1 cuốn sách theo ID
  getBookById: (id: string | number) => axiosClient.get(`/api/books/${id}/`),
  // Tạo sách mới (admin)
  createBook: (data: any) => axiosClient.post('/api/books/', data),
  // Cập nhật toàn bộ thông tin sách
  updateBook: (id: string | number, data: any) => axiosClient.put(`/api/books/${id}/`, data),
  // Cập nhật 1 phần thông tin sách
  patchBook: (id: string | number, data: any) => axiosClient.patch(`/api/books/${id}/`, data),
  // Xóa sách
  deleteBook: (id: string | number) => axiosClient.delete(`/api/books/${id}/`),
};

export default bookService;
