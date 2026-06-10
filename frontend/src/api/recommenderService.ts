import axiosClient from './axiosClient';

const recommenderService = {
  // Lấy gợi ý sách dựa trên lịch sử của khách hàng
  getRecommendations: (customerId: number) =>
    axiosClient.get(`/api/recommendations/${customerId}/`),
};

export default recommenderService;
