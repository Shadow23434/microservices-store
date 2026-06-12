import axiosClient from './axiosClient';

const recommenderService = {
  // Lấy gợi ý sản phẩm dựa trên lịch sử của khách hàng (multi-signal)
  getRecommendations: (customerId: number) =>
    axiosClient.get(`/api/recommendations/${customerId}/`),

  // Lấy sản phẩm tương tự
  getSimilarProducts: (productId: number) =>
    axiosClient.get(`/api/recommendations/similar/${productId}/`),

  // Lấy danh sách wishlist của khách hàng
  getWishlist: (customerId: number) =>
    axiosClient.get(`/api/recommendations/wishlist/`, { params: { customer_id: customerId } }),

  // Thêm sản phẩm vào wishlist
  addToWishlist: (customerId: number, productId: number) =>
    axiosClient.post(`/api/recommendations/wishlist/`, {
      customer_id: customerId,
      product_id: productId,
    }),

  // Xóa sản phẩm khỏi wishlist
  removeFromWishlist: (customerId: number, productId: number) =>
    axiosClient.delete(`/api/recommendations/wishlist/${customerId}/${productId}/`),

  // Gửi tin nhắn chatbot
  sendChatMessage: (data: { message: string; customer_id: number; session_id?: string }) =>
    axiosClient.post(`/api/chat/`, data),

  // Lấy lịch sử chat
  getChatHistory: (conversationId: number) =>
    axiosClient.get(`/api/chat/${conversationId}/`),
};

export default recommenderService;
