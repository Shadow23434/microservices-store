import axiosClient from './axiosClient';

const shipmentService = {
  // Lấy danh sách vận chuyển
  getShipments: () => axiosClient.get('/api/shipments/'),
  // Lấy chi tiết 1 lô hàng
  getShipment: (id: number) => axiosClient.get(`/api/shipments/${id}/`),
  // Tạo vận chuyển mới
  // data: { order_id, customer_id, address }
  createShipment: (data: any) => axiosClient.post('/api/shipments/', data),
};

export default shipmentService;
