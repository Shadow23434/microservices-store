import React, { createContext, useContext, useState, useEffect } from 'react';
import { Review } from '../types';

interface ReviewContextType {
  reviews: Review[];
  addReview: (review: Review) => void;
  getReviewsByProductId: (productId: number) => Review[];
  getUserReviews: (userId: string) => Review[];
}

const ReviewContext = createContext<ReviewContextType | undefined>(undefined);

export function ReviewProvider({ children }: { children: React.ReactNode }) {
  const [reviews, setReviews] = useState<Review[]>(() => {
    const saved = localStorage.getItem('reviews');
    if (saved) return JSON.parse(saved);
    
    // Default mock reviews
    return [
      {
        id: 'rev-1',
        product_id: 1,
        productName: "The Midnight Library",
        productImage: "https://picsum.photos/seed/bookdetail/400/600",
        userId: 'user-1',
        userName: 'Jane Doe',
        rating: 5,
        date: 'March 10, 2026',
        content: 'Absolutely loved this book! It made me rethink all my life choices in the best way possible.'
      }
    ];
  });

  useEffect(() => {
    localStorage.setItem('reviews', JSON.stringify(reviews));
  }, [reviews]);

  const addReview = (review: Review) => {
    setReviews(prev => [review, ...prev]);
  };

  const getReviewsByProductId = (productId: number) => {
    return reviews.filter(r => Number(r.product_id) === Number(productId));
  };

  const getUserReviews = (userId: string) => {
    return reviews.filter(r => r.userId === userId);
  };

  return (
    <ReviewContext.Provider value={{ reviews, addReview, getReviewsByProductId, getUserReviews }}>
      {children}
    </ReviewContext.Provider>
  );
}

export function useReviews() {
  const context = useContext(ReviewContext);
  if (context === undefined) {
    throw new Error('useReviews must be used within a ReviewProvider');
  }
  return context;
}
