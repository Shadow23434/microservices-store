import axiosClient from './axiosClient';

const paymentService = {
  // Lấy danh sách thanh toán
  getPayments: () => axiosClient.get('/api/payments/'),
  // Lấy chi tiết 1 thanh toán
  getPayment: (id: number) => axiosClient.get(`/api/payments/${id}/`),
  // Tạo thanh toán mới
  // data: { order_id, customer_id, amount, method }
  createPayment: (data: any) => axiosClient.post('/api/payments/', data),
};

export default paymentService;
