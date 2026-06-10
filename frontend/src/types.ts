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

export interface CartItem extends Book {
  quantity: number;
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
