import React, { createContext, useContext, useState, useEffect } from 'react';
import { Product } from '../types';
import { normalizeProduct } from '../utils/normalizeProduct';

interface WishlistContextType {
  wishlistItems: Product[];
  addToWishlist: (product: Product) => void;
  removeFromWishlist: (productId: number | string) => void;
  isInWishlist: (productId: number | string) => boolean;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

export function WishlistProvider({ children }: { children: React.ReactNode }) {
  const [wishlistItems, setWishlistItems] = useState<Product[]>(() => {
    const saved = localStorage.getItem('wishlist');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('wishlist', JSON.stringify(wishlistItems));
  }, [wishlistItems]);

  const addToWishlist = (product: Product) => {
    setWishlistItems((prev) => {
      if (!prev.some((item) => Number(item.id) === Number(product.id))) {
        const normalized = normalizeProduct(product);
        return [...prev, normalized];
      }
      return prev;
    });
  };

  const removeFromWishlist = (productId: number | string) => {
    setWishlistItems((prev) => prev.filter((item) => Number(item.id) !== Number(productId)));
  };

  const isInWishlist = (productId: number | string) => {
    return wishlistItems.some((item) => Number(item.id) === Number(productId));
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
