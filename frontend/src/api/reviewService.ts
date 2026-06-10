import axiosClient from './axiosClient';

const reviewService = {
  // Lấy danh sách reviews, filter theo book_id hoặc customer_id
  getReviews: (params?: { book_id?: number; customer_id?: number }) =>
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
  // Lấy $iểm trung bình và tổng số review của 1 cuốn sách
  getBookRating: (bookId: number) =>
    axiosClient.get(`/api/reviews/book/${bookId}/rating/`),
};

export default reviewService;
