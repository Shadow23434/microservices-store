export interface Book {
  id: number;
  title: string;
  author: string;
  price: string;
  rating: string;
  reviews: number;
  image: string;
  category: string;
  format: string;
  pages?: number;
  language?: string;
  publisher?: string;
  publicationDate?: string;
  isbn?: string;
  description?: string;
  stock?: number;
}

export type ProductType = 'book' | 'laptop' | 'mobile' | 'cloth';

export interface BookDetail {
  author: string;
  isbn?: string;
  publisher?: string;
  published_date?: string;
  pages?: number;
  language?: string;
}

export interface LaptopDetail {
  brand: string;
  cpu?: string;
  ram_gb?: number;
  storage_gb?: number;
  display_inch?: number;
  os?: string;
  weight_kg?: number;
  gpu?: string;
}

export interface MobileDetail {
  brand: string;
  screen_inch?: number;
  battery_mah?: number;
  ram_gb?: number;
  storage_gb?: number;
  camera_mp?: number;
  os?: string;
}

export interface ClothDetail {
  brand?: string;
  sizes?: string;
  color?: string;
  material?: string;
  gender?: string;
}

export interface Product {
  id: number;
  name: string;
  product_type: ProductType;
  price: string;
  stock: number;
  description: string;
  category_id?: number;
  image_url: string;
  sku: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  detail?: BookDetail | LaptopDetail | MobileDetail | ClothDetail | null;
}

export interface CartItem extends Book {
  quantity: number;
}

export interface CartItemProduct {
  id: number;
  product_id: number;
  product: Product;
  quantity: number;
  unit_price: string;
}

export interface Review {
  id: string;
  bookId: number;
  bookTitle: string;
  bookImage: string;
  userId: string;
  userName: string;
  rating: number;
  date: string;
  content: string;
}

export interface ProductReview {
  id: string;
  product_id: number;
  product_type: string;
  customer_id: number;
  rating: number;
  comment: string;
  created_at: string;
  updated_at: string;
}
