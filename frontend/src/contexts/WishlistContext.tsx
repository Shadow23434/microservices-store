import React, { createContext, useContext, useState, useEffect } from 'react';
import { Book } from '../types';

interface WishlistContextType {
  wishlistItems: Book[];
  addToWishlist: (book: Book) => void;
  removeFromWishlist: (bookId: number | string) => void;
  isInWishlist: (bookId: number | string) => boolean;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

export function WishlistProvider({ children }: { children: React.ReactNode }) {
  const [wishlistItems, setWishlistItems] = useState<Book[]>(() => {
    const saved = localStorage.getItem('wishlist');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('wishlist', JSON.stringify(wishlistItems));
  }, [wishlistItems]);

  const addToWishlist = (book: Book) => {
    setWishlistItems((prev) => {
      if (!prev.some((item) => Number(item.id) === Number(book.id))) {
        return [...prev, book];
      }
      return prev;
    });
  };

  const removeFromWishlist = (bookId: number | string) => {
    setWishlistItems((prev) => prev.filter((item) => Number(item.id) !== Number(bookId)));
  };

  const isInWishlist = (bookId: number | string) => {
    return wishlistItems.some((item) => Number(item.id) === Number(bookId));
  };

  return (
    <WishlistContext.Provider value={{ wishlistItems, addToWishlist, removeFromWishlist, isInWishlist }}>
      {children}
    </WishlistContext.Provider>
  );
}

export function useWishlist() {
  const context = useContext(WishlistContext);
  if (context === undefined) {
    throw new Error('useWishlist must be used within a WishlistProvider');
  }
  return context;
}
