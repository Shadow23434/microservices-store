import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Star, Heart, Share2, ShoppingCart, Truck, ShieldCheck, BookOpen, Clock, Loader2 } from 'lucide-react';
import { useWishlist } from '../contexts/WishlistContext';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import bookService from '../api/bookService';
import reviewService from '../api/reviewService';

export default function BookDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState('description');
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewContent, setReviewContent] = useState('');
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);

  const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();
  const { addToCart } = useCart();

  const [book, setBook] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [averageRating, setAverageRating] = useState<number | null>(null);
  const [totalReviews, setTotalReviews] = useState(0);
  const [isLoadingBook, setIsLoadingBook] = useState(true);
  const [isLoadingReviews, setIsLoadingReviews] = useState(false);
  const [error, setError] = useState('');

  // Tải thông tin sách từ API
  useEffect(() => {
    const loadBook = async () => {
      if (!id) return;
      setIsLoadingBook(true);
      setError('');
      try {
        const [data, ratingData] = await Promise.all([
          bookService.getBookById(id),
          reviewService.getBookRating(Number(id)).catch(() => null)
        ]);
        setBook(data);
        if (ratingData) {
          setAverageRating((ratingData as any).average_rating);
          setTotalReviews((ratingData as any).total_reviews || 0);
        }
      } catch (err) {
        console.error('Failed to load book:', err);
        setError('Không thể tải thông tin sách.');
      } finally {
        setIsLoadingBook(false);
      }
    };
    loadBook();
  }, [id]);

  // Tải reviews và rating khi chuyển sang tab reviews
  useEffect(() => {
    if (activeTab !== 'reviews' || !id) return;
    const loadReviews = async () => {
      setIsLoadingReviews(true);
      try {
        const [reviewsData, ratingData] = await Promise.all([
          reviewService.getReviews({ book_id: Number(id) }) as unknown as any[],
          reviewService.getBookRating(Number(id)) as unknown as any,
        ]);
        setReviews(Array.isArray(reviewsData) ? reviewsData : []);
        if (ratingData) {
          setAverageRating(ratingData.average_rating);
          setTotalReviews(ratingData.total_reviews || 0);
        }
      } catch (err) {
        console.error('Failed to load reviews:', err);
        setReviews([]);
      } finally {
        setIsLoadingReviews(false);
      }
    };
    loadReviews();
  }, [activeTab, id]);

  const handleAddReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewContent.trim() || !id) return;
    setIsSubmittingReview(true);
    try {
      await reviewService.createReview({
        book_id: Number(id),
        customer_id: user?.id || 1,
        rating: reviewRating,
        comment: reviewContent,
      });
      setReviewContent('');
      setReviewRating(5);
      // Tải lại reviews sau khi submit
      const [reviewsData, ratingData] = await Promise.all([
        reviewService.getReviews({ book_id: Number(id) }) as unknown as any[],
        reviewService.getBookRating(Number(id)) as unknown as any,
      ]);
      setReviews(Array.isArray(reviewsData) ? reviewsData : []);
      if (ratingData) {
        setAverageRating(ratingData.average_rating);
        setTotalReviews(ratingData.total_reviews || 0);
      }
    } catch (err) {
      console.error('Failed to submit review:', err);
    } finally {
      setIsSubmittingReview(false);
    }
  };

  if (isLoadingBook) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 flex justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
          <p className="text-gray-500 dark:text-gray-400">Đang tải thông tin sách...</p>
        </div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-red-600 dark:text-red-400 text-lg mb-4">{error || 'Không tìm thấy sách.'}</p>
        <Link to="/catalog" className="text-indigo-600 hover:text-indigo-500 font-medium">← Quay lại Catalog</Link>
      </div>
    );
  }

  // Phân tích tên trường từ backend (có thể khác nhau)
  const bookImage = book.image || book.cover_image || `https://picsum.photos/seed/book${book.id}/400/600`;
  const rawRating = averageRating !== null && averageRating !== undefined ? averageRating : Number(book.rating || 0);
  const bookRating = Number(rawRating).toFixed(1);
  const bookStock = book.stock || book.stock_quantity || 15;

  return (
    <div className="bg-white dark:bg-gray-950 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumbs */}
        <nav className="flex text-sm text-gray-500 dark:text-gray-400 mb-8">
          <Link to="/" className="hover:text-indigo-600 dark:hover:text-indigo-400">Home</Link>
          <span className="mx-2">/</span>
          <Link to="/catalog" className="hover:text-indigo-600 dark:hover:text-indigo-400">Catalog</Link>
          <span className="mx-2">/</span>
          <Link to={`/catalog?category=${book.category}`} className="hover:text-indigo-600 dark:hover:text-indigo-400">{book.category}</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900 dark:text-white font-medium truncate">{book.title}</span>
        </nav>

        <div className="flex flex-col lg:flex-row gap-12">
          {/* Product Image */}
          <div className="w-full lg:w-1/3 flex-shrink-0">
            <div className="sticky top-24">
              <div className="bg-gray-100 dark:bg-gray-900 rounded-2xl p-8 flex items-center justify-center transition-colors duration-200">
                <img
                  src={bookImage}
                  alt={book.title}
                  className="w-full max-w-sm rounded-lg shadow-2xl"
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="mt-6 flex justify-center gap-4">
                <button
                  onClick={() => {
                    if (isInWishlist(book.id)) {
                      removeFromWishlist(book.id);
                    } else {
                      addToWishlist({ ...book, image: bookImage, format: 'Paperback' });
                    }
                  }}
                  className={`flex items-center justify-center gap-2 px-4 py-2 border rounded-lg font-medium w-full transition-colors ${
                    isInWishlist(book.id)
                      ? 'border-red-200 bg-red-50 text-red-600 dark:border-red-900/30 dark:bg-red-900/20 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40'
                      : 'border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                >
                  <Heart className={`h-5 w-5 ${isInWishlist(book.id) ? 'fill-current' : ''}`} />
                  {isInWishlist(book.id) ? 'In Wishlist' : 'Add to Wishlist'}
                </button>
                <button className="flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 font-medium w-full transition-colors">
                  <Share2 className="h-5 w-5" /> Share
                </button>
              </div>
            </div>
          </div>

          {/* Product Info */}
          <div className="w-full lg:w-2/3">
            <div className="mb-6">
              <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white mb-2">{book.title}</h1>
              <p className="text-xl text-gray-600 dark:text-gray-400 mb-4">by <Link to="#" className="text-indigo-600 dark:text-indigo-400 hover:underline">{book.author}</Link></p>

              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`h-5 w-5 ${i < Math.floor(Number(bookRating)) ? 'text-yellow-400 fill-current' : 'text-gray-300 dark:text-gray-600'}`} />
                  ))}
                  <span className="ml-2 text-sm font-medium text-gray-900 dark:text-white">{bookRating}</span>
                </div>
                <span className="text-gray-300 dark:text-gray-700">|</span>
                <button onClick={() => setActiveTab('reviews')} className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
                  {totalReviews || book.reviews || 0} Reviews
                </button>
                <span className="text-gray-300 dark:text-gray-700">|</span>
                <span className="text-sm text-green-600 font-medium">In Stock ({bookStock} available)</span>
              </div>

              <div className="text-4xl font-bold text-gray-900 dark:text-white mb-8">${book.price}</div>
            </div>

            {/* Formats */}
            <div className="mb-8">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Format</h3>
              <div className="flex flex-wrap gap-3">
                {Array.from(new Set(['Hardcover', 'Paperback', 'E-Book', 'Audiobook'].concat(book.format ? [book.format] : []))).map((fmt) => (
                  <button 
                    key={fmt} 
                    className={`px-5 py-3 border rounded-xl font-medium flex flex-col items-start transition-colors ${
                      book.format === fmt 
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700 dark:border-indigo-500 dark:bg-indigo-900/20 dark:text-indigo-400' 
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <span>{fmt}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Add to Cart Actions */}
            <div className="flex flex-col sm:flex-row gap-4 mb-10 pb-10 border-b border-gray-200 dark:border-gray-800">
              <div className="flex items-center border border-gray-300 dark:border-gray-700 rounded-lg h-14">
                <button
                  className="px-4 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white h-full flex items-center justify-center transition-colors"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                >-</button>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-16 text-center font-medium text-gray-900 dark:text-white bg-transparent border-x border-gray-300 dark:border-gray-700 h-full focus:outline-none"
                />
                <button
                  className="px-4 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white h-full flex items-center justify-center transition-colors"
                  onClick={() => setQuantity(Math.min(bookStock, quantity + 1))}
                >+</button>
              </div>
              <button
                onClick={() => addToCart({ ...book, image: bookImage, format: 'Paperback' }, quantity)}
                className="flex-1 bg-indigo-600 text-white h-14 rounded-lg font-bold text-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2 shadow-sm"
              >
                <ShoppingCart className="h-5 w-5" /> Add to Cart
              </button>
              <button
                onClick={() => {
                  addToCart({ ...book, image: bookImage, format: 'Paperback' }, quantity);
                  navigate('/cart');
                }}
                className="flex-1 bg-gray-900 dark:bg-gray-800 text-white h-14 rounded-lg font-bold text-lg hover:bg-gray-800 dark:hover:bg-gray-700 transition-colors flex items-center justify-center shadow-sm"
              >
                Buy Now
              </button>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
              <div className="flex items-start gap-3">
                <div className="bg-indigo-50 dark:bg-indigo-900/30 p-2 rounded-lg text-indigo-600 dark:text-indigo-400">
                  <Truck className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Free Shipping</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">On orders over $35</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-indigo-50 dark:bg-indigo-900/30 p-2 rounded-lg text-indigo-600 dark:text-indigo-400">
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Secure Payment</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">100% secure checkout</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-indigo-50 dark:bg-indigo-900/30 p-2 rounded-lg text-indigo-600 dark:text-indigo-400">
                  <Clock className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Easy Returns</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">30 days return policy</p>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div>
              <div className="border-b border-gray-200 dark:border-gray-800">
                <nav className="-mb-px flex space-x-8">
                  {['description', 'details', 'reviews'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`${activeTab === tab ? 'border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-lg transition-colors capitalize`}
                    >
                      {tab === 'reviews' ? `Reviews (${totalReviews || book.reviews || 0})` : tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </nav>
              </div>
              <div className="py-6">
                {activeTab === 'description' && (
                  <div className="prose prose-indigo dark:prose-invert max-w-none text-gray-600 dark:text-gray-400">
                    <p>{book.description || book.synopsis || 'No description available.'}</p>
                  </div>
                )}
                {activeTab === 'details' && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4 text-sm">
                    {[
                      ['Publisher', book.publisher],
                      ['Publication Date', book.published_date || book.publicationDate],
                      ['Language', book.language || 'English'],
                      ['Pages', book.pages || book.page_count],
                      ['ISBN', book.isbn],
                      ['Category', book.category],
                    ].filter(([, val]) => val).map(([label, val]) => (
                      <div key={label} className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-800">
                        <span className="text-gray-500 dark:text-gray-400">{label}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{val}</span>
                      </div>
                    ))}
                  </div>
                )}
                {activeTab === 'reviews' && (
                  <div>
                    <div className="flex items-center gap-4 mb-8">
                      <div className="text-5xl font-bold text-gray-900 dark:text-white">
                        {averageRating != null ? Number(averageRating).toFixed(1) : '0.0'}
                      </div>
                      <div>
                        <div className="flex text-yellow-400 mb-1">
                          {[...Array(5)].map((_, i) => (
                            <Star key={i} className={`h-5 w-5 ${i < Math.round(Number(averageRating || 0)) ? 'fill-current' : 'text-gray-300 dark:text-gray-600'}`} />
                          ))}
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Based on {totalReviews} reviews</p>
                      </div>
                    </div>

                    {/* Write a Review Form */}
                    <div className="bg-gray-50 dark:bg-gray-800/50 rounded-2xl p-6 mb-8 border border-gray-100 dark:border-gray-700">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Write a Review</h3>
                      <form onSubmit={handleAddReview}>
                        <div className="mb-4">
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Rating</label>
                          <div className="flex gap-2">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                type="button"
                                onClick={() => setReviewRating(star)}
                                className={`p-1 transition-colors ${reviewRating >= star ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
                              >
                                <Star className="h-8 w-8 fill-current" />
                              </button>
                            ))}
                          </div>
                        </div>
                        <div className="mb-4">
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Review</label>
                          <textarea
                            rows={4}
                            value={reviewContent}
                            onChange={(e) => setReviewContent(e.target.value)}
                            placeholder="What did you think about this book?"
                            className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-3 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                            required
                          />
                        </div>
                        <button
                          type="submit"
                          disabled={isSubmittingReview}
                          className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-70 flex items-center gap-2"
                        >
                          {isSubmittingReview && <Loader2 className="h-4 w-4 animate-spin" />}
                          Submit Review
                        </button>
                      </form>
                    </div>

                    {/* Reviews List */}
                    {isLoadingReviews ? (
                      <div className="flex justify-center py-8">
                        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {reviews.length === 0 ? (
                          <p className="text-gray-500 dark:text-gray-400">No reviews yet. Be the first to review this book!</p>
                        ) : (
                          reviews.map((review: any) => (
                            <div key={review.id} className="border-t border-gray-200 dark:border-gray-800 pt-6">
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                  <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/50 rounded-full flex items-center justify-center text-indigo-700 dark:text-indigo-300 font-bold">
                                    {(review.customer_name || review.user_name || `C${review.customer_id}`).charAt(0).toUpperCase()}
                                  </div>
                                  <div>
                                    <h5 className="font-medium text-gray-900 dark:text-white">
                                      {review.customer_name || review.user_name || `Customer #${review.customer_id}`}
                                    </h5>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                      {review.created_at ? new Date(review.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : ''}
                                    </p>
                                  </div>
                                </div>
                                <div className="flex text-yellow-400">
                                  {[...Array(5)].map((_, i) => (
                                    <Star key={i} className={`h-4 w-4 ${i < review.rating ? 'fill-current' : 'text-gray-300 dark:text-gray-600'}`} />
                                  ))}
                                </div>
                              </div>
                              <p className="text-gray-600 dark:text-gray-400 text-sm mt-3">{review.comment || review.content || ''}</p>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
