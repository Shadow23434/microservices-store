import axiosClient from './axiosClient';

const reviewService = {
  // Lấy danh sách reviews, filter theo product_id hoặc customer_id
  getReviews: (params?: { product_id?: number; customer_id?: number }) =>
    axiosClient.get('/api/reviews/', { params }),
  // Lấy chi tiết 1 review
  getReviewById: (id: number) => axiosClient.get(`/api/reviews/${id}/`),
  // Tạo review mới
  // data: { book_id, customer_id, rating, comment }
  createReview: (data: any) => axiosClient.post('/api/reviews/', data),
  // Cập nhật review
  updateReview: (id: number, data: any) => axiosClient.put(`/api/reviews/${id}/`, data),
  // Xóa review
  deleteReview: (id: number) => axiosClient.delete(`/api/reviews/${id}/`),
  // Lấy điểm trung bình và tổng số review của 1 sản phẩm
  getProductRating: (productId: number) =>
    axiosClient.get(`/api/reviews/?product_id=${productId}`),
};

export default reviewService;
