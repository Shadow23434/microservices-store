import axiosClient from './axiosClient';

// Cart service routes:
// GET  /api/carts/{customer_id}/   → Xem giỏ hàng của customer
// POST /api/carts/                 → Tạo giỏ hàng cho customer mới (auto gọi khi register)
// POST /api/cart-items/            → Thêm item vào giỏ hàng

const cartService = {
  // Lấy giỏ hàng của customer theo customer_id
  getCart: (customerId: number) => axiosClient.get(`/api/carts/${customerId}/`),
  // Tạo giỏ hàng rỗng cho customer
  createCart: (customerId: number) =>
    axiosClient.post('/api/carts/', { customer_id: customerId }),
  // Thêm sách vào giỏ
  // data: { cart_id, book_id, quantity }
  addToCart: (data: any) => axiosClient.post('/api/cart-items/', data),
};

export default cartService;
