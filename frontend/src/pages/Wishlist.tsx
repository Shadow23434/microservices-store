import React from 'react';
import { Link } from 'react-router-dom';
import { Trash2, ShoppingCart, HeartCrack } from 'lucide-react';
import { useWishlist } from '../contexts/WishlistContext';
import { useCart } from '../contexts/CartContext';

export default function Wishlist() {
  const { wishlistItems, removeFromWishlist } = useWishlist();
  const { addToCart } = useCart();

  if (wishlistItems.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 transition-colors duration-200">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
            <HeartCrack className="h-12 w-12 text-gray-400 dark:text-gray-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Your wishlist is empty</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
            Looks like you haven't added any products to your wishlist yet. Explore our catalog to find your next great read!
          </p>
          <Link
            to="/catalog"
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
          >
            Browse Products
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 transition-colors duration-200">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Wishlist</h1>
        <span className="text-gray-600 dark:text-gray-400">
          {wishlistItems.length} {wishlistItems.length === 1 ? 'item' : 'items'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {wishlistItems.map((book) => (
          <div key={book.id} className="bg-white dark:bg-gray-950 rounded-2xl overflow-hidden shadow-sm border border-gray-200 dark:border-gray-800 flex flex-col transition-colors duration-200">
            <Link to={`/product/${book.id}`} className="block aspect-w-2 aspect-h-3 bg-gray-200 dark:bg-gray-800 relative group overflow-hidden">
              <img
                src={book.image}
                alt={book.title}
                className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                referrerPolicy="no-referrer"
              />
            </Link>
            <div className="p-4 flex flex-col flex-grow">
              <div className="mb-1">
                <p className="text-xs font-medium text-indigo-600 dark:text-indigo-400">{book.category}</p>
              </div>
              <Link to={`/product/${book.id}`} className="block mb-1">
                <h3 className="text-base font-bold text-gray-900 dark:text-white line-clamp-1 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">{book.title}</h3>
              </Link>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{book.author}</p>
              
              <div className="mt-auto flex items-center justify-between">
                <span className="text-lg font-bold text-gray-900 dark:text-white">${book.price}</span>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => removeFromWishlist(book.id)}
                    className="p-2 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-colors rounded-full hover:bg-red-50 dark:hover:bg-red-900/20"
                    title="Remove from wishlist"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                  <button 
                    onClick={() => {
                      addToCart(book);
                      removeFromWishlist(book.id);
                    }}
                    className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full transition-colors shadow-sm"
                    title="Add to cart"
                  >
                    <ShoppingCart className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
