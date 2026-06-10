import axiosClient from './axiosClient';

const productService = {
  // Lấy danh sách tất cả sản phẩm, có thể filter theo product_type
  getAllProducts: (params?: any) => axiosClient.get('/api/products/', { params }),
  // Lấy chi tiết 1 sản phẩm theo ID
  getProductById: (id: string | number) => axiosClient.get(`/api/products/${id}/`),
  // Tạo sản phẩm mới (admin)
  createProduct: (data: any) => axiosClient.post('/api/products/', data),
  // Cập nhật toàn bộ thông tin sản phẩm
  updateProduct: (id: string | number, data: any) => axiosClient.put(`/api/products/${id}/`, data),
  // Cập nhật 1 phần thông tin sản phẩm
  patchProduct: (id: string | number, data: any) => axiosClient.patch(`/api/products/${id}/`, data),
  // Xóa sản phẩm
  deleteProduct: (id: string | number) => axiosClient.delete(`/api/products/${id}/`),
  // Convenience methods for specific product types
  getBooks: () => axiosClient.get('/api/products/', { params: { product_type: 'book' } }),
  getLaptops: () => axiosClient.get('/api/products/', { params: { product_type: 'laptop' } }),
  getMobiles: () => axiosClient.get('/api/products/', { params: { product_type: 'mobile' } }),
  getClothes: () => axiosClient.get('/api/products/', { params: { product_type: 'cloth' } }),
};

export default productService;