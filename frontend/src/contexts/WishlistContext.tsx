import React, { createContext, useContext, useState, useEffect } from 'react';
import { Product } from '../types';
import { normalizeProduct } from '../utils/normalizeProduct';
import recommenderService from '../api/recommenderService';
import { useAuth } from './AuthContext';

interface WishlistContextType {
  wishlistItems: Product[];
  addToWishlist: (product: Product) => void;
  removeFromWishlist: (productId: number | string) => void;
  isInWishlist: (productId: number | string) => boolean;
  loadWishlist: () => Promise<void>;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

export function WishlistProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [wishlistItems, setWishlistItems] = useState<Product[]>(() => {
    const saved = localStorage.getItem('wishlist');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('wishlist', JSON.stringify(wishlistItems));
  }, [wishlistItems]);

  // Load wishlist from backend when user logs in
  const loadWishlist = async () => {
    if (!isAuthenticated || !user?.id) return;

    try {
      const response = await recommenderService.getWishlist(user.id) as any;
      if (response?.wishlist_items && Array.isArray(response.wishlist_items)) {
        // Convert backend wishlist to Product format
        const items: Product[] = response.wishlist_items.map((item: any) => ({
          id: item.product_id,
          product_type: 'book', // Default, will be enriched if needed
        }));
        setWishlistItems(items);
      }
    } catch (err) {
      console.error('Failed to load wishlist from backend:', err);
    }
  };

  // Load wishlist when user authenticates
  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadWishlist();
    }
  }, [isAuthenticated, user?.id]);

  const addToWishlist = async (product: Product) => {
    const productId = Number(product.id);

    // Update local state first
    setWishlistItems((prev) => {
      if (!prev.some((item) => Number(item.id) === productId)) {
        const normalized = normalizeProduct(product);
        return [...prev, normalized];
      }
      return prev;
    });

    // Sync to backend if authenticated
    if (isAuthenticated && user?.id) {
      try {
        await recommenderService.addToWishlist(user.id, productId);
      } catch (err) {
        console.error('Failed to add to backend wishlist:', err);
      }
    }
  };

  const removeFromWishlist = async (productId: number | string) => {
    const pid = Number(productId);

    // Update local state first
    setWishlistItems((prev) => prev.filter((item) => Number(item.id) !== pid));

    // Sync to backend if authenticated
    if (isAuthenticated && user?.id) {
      try {
        await recommenderService.removeFromWishlist(user.id, pid);
      } catch (err) {
        console.error('Failed to remove from backend wishlist:', err);
      }
    }
  };

  const isInWishlist = (productId: number | string) => {
    return wishlistItems.some((item) => Number(item.id) === Number(productId));
  };

  return (
    <WishlistContext.Provider value={{ wishlistItems, addToWishlist, removeFromWishlist, isInWishlist, loadWishlist }}>
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
