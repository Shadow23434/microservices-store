import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Star, ArrowRight, BookOpen, TrendingUp, Award, ShoppingCart, Heart, Sparkles, Loader2 } from 'lucide-react';
import { useWishlist } from '../contexts/WishlistContext';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import productService from '../api/productService';
import catalogService from '../api/catalogService';
import recommenderService from '../api/recommenderService';
import reviewService from '../api/reviewService';

function User(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

const CATEGORY_ICONS: Record<string, any> = {
  'Fiction': BookOpen,
  'Non-Fiction': BookOpen,
  'Science Fiction': TrendingUp,
  'Sci-Fi': TrendingUp,
  'Mystery': Award,
  'Mystery & Thriller': Award,
  'Biography': User,
  'Self-Help': Star,
};

export default function Home() {
  const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();
  const { addToCart } = useCart();
  const { user } = useAuth();

  const [featuredProducts, setFeaturedProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [recommendations, setRecommendations] = useState<any[]>([]);

  // Tải sản phẩm và categories từ API
  useEffect(() => {
    const loadData = async () => {
      setIsLoadingProducts(true);
      try {
        const [productsData, categoriesData] = await Promise.all([
          productService.getAllProducts() as unknown as any[],
          catalogService.getCategories() as unknown as any[],
        ]);

        const initialProducts = (productsData || []).slice(0, 8);

        // Lấy rating song song cho các sản phẩm
        const productsWithRating = await Promise.all(
          initialProducts.map(async (product: any) => {
            try {
              const ratingData = await reviewService.getBookRating(product.id) as any;
              if (ratingData && ratingData.average_rating !== null) {
                return { ...product, rating: ratingData.average_rating, reviews: ratingData.total_reviews };
              }
            } catch(e) {}
            return product;
          })
        );

        setFeaturedProducts(productsWithRating);
        setCategories((categoriesData || []).slice(0, 6));
      } catch (err) {
        console.error('Failed to load home data:', err);
        setFeaturedProducts([]);
        setCategories([]);
      } finally {
        setIsLoadingProducts(false);
      }
    };
    loadData();
  }, []);

  const handleGetRecommendations = async () => {
    setIsGenerating(true);
    setRecommendations([]);
    try {
      let recsToProcess = [];
      if (user?.id) {
        // Gửi API recommender thật nếu user đã đăng nhập
        const recs = await recommenderService.getRecommendations(user.id) as unknown as any[];
        recsToProcess = Array.isArray(recs) ? recs.slice(0, 3) : [];
      } else {
        // Fallback: lấy random 3 sách từ danh sách
        const allBooks = await productService.getBooks() as unknown as any[];
        const shuffled = [...(allBooks || [])].sort(() => 0.5 - Math.random());
        recsToProcess = shuffled.slice(0, 3);
      }
      
      const recsWithRating = await Promise.all(
        recsToProcess.map(async (product: any) => {
          try {
            const ratingData = await reviewService.getBookRating(product.id) as any;
            if (ratingData && ratingData.average_rating !== null) {
              return { ...product, rating: ratingData.average_rating, reviews: ratingData.total_reviews };
            }
          } catch(e) {}
          return product;
        })
      );

      setRecommendations(recsWithRating);
    } catch (err) {
      console.error('Failed to get recommendations:', err);
      // Fallback to featured products subset
      setRecommendations(featuredProducts.slice(0, 3));
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-950 transition-colors duration-200">
      {/* Hero Section */}
      <div className="relative bg-indigo-900 overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="https://picsum.photos/seed/library/1920/1080"
            alt="Library background"
            className="w-full h-full object-cover opacity-20"
            referrerPolicy="no-referrer"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-900 to-transparent mix-blend-multiply" />
        </div>
        <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-serif font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Discover Your Next<br />Great Adventure
          </h1>
          <p className="mt-6 text-xl text-indigo-100 max-w-3xl">
            Explore millions of books, from timeless classics to the latest bestsellers.
            Join our community of readers and find the stories that speak to you.
          </p>
          <div className="mt-10 flex gap-4">
            <Link
              to="/catalog"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-900 bg-white hover:bg-gray-50 transition-colors"
            >
              Shop Now
            </Link>
            <Link
              to="/catalog?sort=new"
              className="inline-flex items-center px-6 py-3 border border-white text-base font-medium rounded-md text-white hover:bg-white/10 transition-colors"
            >
              New Arrivals
            </Link>
          </div>
        </div>
      </div>

      {/* Categories Section */}
      <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Browse by Category</h2>
            <p className="mt-1 text-gray-500 dark:text-gray-400">Find products in your favorite genres</p>
          </div>
          <Link to="/catalog" className="hidden sm:flex items-center text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium transition-colors">
            View All Categories <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </div>
        {categories.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {categories.map((category: any) => {
              const catName = category.name || category.category_name || category.title || 'Category';
              const Icon = CATEGORY_ICONS[catName] || BookOpen;
              return (
                <Link
                  key={category.id || catName}
                  to={`/catalog?category=${catName}`}
                  className="group flex flex-col items-center p-6 bg-gray-50 dark:bg-gray-900 rounded-2xl hover:bg-indigo-50 dark:hover:bg-gray-800 transition-colors border border-gray-100 dark:border-gray-800 hover:border-indigo-100 dark:hover:border-gray-700"
                >
                  <div className="w-12 h-12 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform text-indigo-600 dark:text-indigo-400 mb-4">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white text-center">{catName}</h3>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {['Fiction', 'Non-Fiction', 'Sci-Fi', 'Mystery', 'Biography', 'Self-Help'].map((cat) => {
              const Icon = CATEGORY_ICONS[cat] || BookOpen;
              return (
                <Link key={cat} to={`/catalog?category=${cat}`}
                  className="group flex flex-col items-center p-6 bg-gray-50 dark:bg-gray-900 rounded-2xl hover:bg-indigo-50 dark:hover:bg-gray-800 transition-colors border border-gray-100 dark:border-gray-800">
                  <div className="w-12 h-12 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform text-indigo-600 dark:text-indigo-400 mb-4">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white text-center">{cat}</h3>
                </Link>
              );
            })}
          </div>
        )}
      </div>

      {/* Featured Books Section */}
      <div className="bg-gray-50 dark:bg-gray-900 py-16 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Bestselling Products</h2>
              <p className="mt-1 text-gray-500 dark:text-gray-400">The most popular products this week</p>
            </div>
            <Link to="/catalog" className="hidden sm:flex items-center text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium transition-colors">
              View All <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </div>

          {isLoadingProducts ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {featuredProducts.map((product: any) => (
                <div key={product.id} className="group flex flex-col bg-white dark:bg-gray-950 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-800 relative">
                  <Link to={`/product/${product.id}`} className="block aspect-w-2 aspect-h-3 bg-gray-200 dark:bg-gray-800 overflow-hidden">
                    <img
                      src={product.image || product.image_url || product.cover_image || `https://picsum.photos/seed/product${product.id}/200/300`}
                      alt={product.title || product.name}
                      className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                      referrerPolicy="no-referrer"
                    />
                  </Link>
                  {/* Wishlist Button */}
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      if (isInWishlist(product.id)) {
                        removeFromWishlist(product.id);
                      } else {
                        addToWishlist({ ...product, format: 'Paperback' });
                      }
                    }}
                    className="absolute top-3 right-3 p-2 rounded-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm hover:bg-white dark:hover:bg-gray-900 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-colors shadow-sm z-10"
                  >
                    <Heart className={`h-4 w-4 ${isInWishlist(product.id) ? 'fill-red-500 text-red-500' : ''}`} />
                  </button>
                  <div className="p-5 flex flex-col flex-grow">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-xs font-medium text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">{product.category || product.product_type || 'General'}</p>
                      <div className="flex items-center">
                        <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span className="ml-1 text-sm text-gray-600 dark:text-gray-400">{Number(product.rating || 0).toFixed(1)}</span>
                      </div>
                    </div>
                    <Link to={`/product/${product.id}`} className="block">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1 line-clamp-1 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">{product.title || product.name}</h3>
                    </Link>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{product.author || product.detail?.brand || product.description?.substring(0, 50)}</p>
                    <div className="mt-auto flex items-center justify-between">
                      <span className="text-lg font-bold text-gray-900 dark:text-white">${product.price || '0.00'}</span>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          addToCart({ ...product, format: 'Paperback' });
                        }}
                        className="bg-gray-900 dark:bg-gray-800 text-white p-2 rounded-full hover:bg-indigo-600 dark:hover:bg-indigo-500 transition-colors"
                      >
                        <ShoppingCart className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* AI Recommended Section */}
      <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-indigo-50 dark:from-indigo-900/20 to-purple-50 dark:to-purple-900/20 rounded-3xl p-8 sm:p-12 flex flex-col md:flex-row items-center justify-between border border-indigo-100 dark:border-indigo-900/30">
          <div className="md:w-1/2 mb-8 md:mb-0 md:pr-8">
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-200 text-sm font-semibold mb-4">
              <Sparkles className="h-4 w-4 mr-2" /> AI Powered
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Personalized Recommendations</h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
              Tell us what you like, and our AI will find the perfect next read for you. We analyze millions of data points to suggest products you'll love.
            </p>
            <button
              onClick={handleGetRecommendations}
              disabled={isGenerating}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Analyzing your taste...
                </>
              ) : (
                'Get Recommendations'
              )}
            </button>
          </div>
          <div className="md:w-1/2 relative min-h-[300px] flex items-center justify-center">
            {recommendations.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
                {recommendations.map((book: any) => (
                  <Link key={book.id} to={`/product/${book.id}`} className="group flex flex-col bg-white dark:bg-gray-900 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-all border border-gray-100 dark:border-gray-800">
                    <div className="aspect-w-2 aspect-h-3 bg-gray-200 dark:bg-gray-800 overflow-hidden">
                      <img
                        src={book.image || book.cover_image || `https://picsum.photos/seed/book${book.id}/200/300`}
                        alt={book.title}
                        className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                        referrerPolicy="no-referrer"
                      />
                    </div>
                    <div className="p-3 flex flex-col flex-grow">
                      <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-1 line-clamp-1 group-hover:text-indigo-600 transition-colors">{book.title}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 line-clamp-1">{book.author}</p>
                      <div className="mt-auto flex items-center justify-between">
                        <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400">${book.price || '0.00'}</span>
                        <div className="flex items-center">
                          <Star className="h-3 w-3 text-yellow-400 fill-current" />
                            <span className="ml-1 text-xs text-gray-600 dark:text-gray-400">{Number(book.rating || 0).toFixed(1)}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4 w-full max-w-[300px] mx-auto transition-opacity duration-300" style={{ opacity: isGenerating ? 0.3 : 1 }}>
                <img src="https://picsum.photos/seed/book5/200/300" alt="Book" className="rounded-lg shadow-md transform rotate-[-5deg] translate-y-4" referrerPolicy="no-referrer" />
                <img src="https://picsum.photos/seed/book6/200/300" alt="Book" className="rounded-lg shadow-md transform rotate-[5deg] -translate-y-4" referrerPolicy="no-referrer" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
