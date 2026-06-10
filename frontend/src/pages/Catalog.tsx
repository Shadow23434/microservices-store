import { useState, useMemo, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Star, Filter, ChevronDown, Check, ShoppingCart, SearchX, Heart, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { useWishlist } from '../contexts/WishlistContext';
import { useCart } from '../contexts/CartContext';
import bookService from '../api/bookService';
import catalogService from '../api/catalogService';

const FORMATS = ["Hardcover", "Paperback", "E-Book", "Audiobook"];
const ITEMS_PER_PAGE = 6;

export default function Catalog() {
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get('search') || '';
  const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();
  const { addToCart } = useCart();

  const [books, setBooks] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [selectedCategory, setSelectedCategory] = useState("All");
  const [priceRange, setPriceRange] = useState([0, 50]);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState("Most Popular");

  // Tải sách và categories từ API
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [booksData, categoriesData] = await Promise.all([
          bookService.getAllBooks() as unknown as any[],
          catalogService.getCategories() as unknown as any[],
        ]);
        setBooks(booksData || []);
        setCategories(categoriesData || []);
      } catch (err) {
        console.error('Failed to load catalog data:', err);
        setError('Failed to load catalog data.');
        setBooks([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedCategory, priceRange, sortBy]);

  const ALL_CATEGORIES = ['All', ...categories.map((c: any) => c.name || c.category_name || c.title || '').filter(Boolean)];

  const filteredBooks = useMemo(() => {
    let result = books.filter((book: any) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesTitle = (book.title || '').toLowerCase().includes(query);
        const matchesAuthor = (book.author || '').toLowerCase().includes(query);
        if (!matchesTitle && !matchesAuthor) return false;
      }
      if (selectedCategory !== "All" && book.category !== selectedCategory) {
        return false;
      }
      if (parseFloat(book.price || '0') > priceRange[1]) {
        return false;
      }
      return true;
    });

    switch (sortBy) {
      case "Price: Low to High":
        result.sort((a: any, b: any) => parseFloat(a.price || '0') - parseFloat(b.price || '0'));
        break;
      case "Price: High to Low":
        result.sort((a: any, b: any) => parseFloat(b.price || '0') - parseFloat(a.price || '0'));
        break;
      case "Highest Rated":
        result.sort((a: any, b: any) => parseFloat(b.rating || '0') - parseFloat(a.rating || '0'));
        break;
      case "Newest Arrivals":
        result.sort((a: any, b: any) => {
          const dateA = a.published_date || a.publicationDate ? new Date(a.published_date || a.publicationDate).getTime() : 0;
          const dateB = b.published_date || b.publicationDate ? new Date(b.published_date || b.publicationDate).getTime() : 0;
          if (dateA !== dateB) return dateB - dateA;
          return b.id - a.id;
        });
        break;
      case "Most Popular":
      default:
        result.sort((a: any, b: any) => (b.reviews_count || b.reviews || 0) - (a.reviews_count || a.reviews || 0));
        break;
    }
    return result;
  }, [books, searchQuery, selectedCategory, priceRange, sortBy]);

  const totalPages = Math.ceil(filteredBooks.length / ITEMS_PER_PAGE);
  const paginatedBooks = filteredBooks.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 flex justify-center">
        <div className="flex flex-col items-center gap-4 text-gray-500 dark:text-gray-400">
          <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
          <p className="text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <p className="text-red-600 dark:text-red-400 text-lg mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-colors duration-200">
      {/* Breadcrumbs */}
      <nav className="flex text-sm text-gray-500 dark:text-gray-400 mb-8">
        <Link to="/" className="hover:text-indigo-600 dark:hover:text-indigo-400">Home</Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900 dark:text-white font-medium">Catalog</span>
      </nav>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Filters */}
        <div className="w-full lg:w-64 flex-shrink-0">
          <div className="bg-white dark:bg-gray-950 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 sticky top-24 transition-colors duration-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Filters</h2>
              <Filter className="h-5 w-5 text-gray-500 dark:text-gray-400" />
            </div>

            {/* Categories */}
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Categories</h3>
              <div className="space-y-3">
                {ALL_CATEGORIES.map(category => (
                  <label key={category} className="flex items-center cursor-pointer group">
                    <div className={`w-5 h-5 rounded border flex items-center justify-center mr-3 transition-colors ${selectedCategory === category ? 'bg-indigo-600 border-indigo-600' : 'border-gray-300 dark:border-gray-600 group-hover:border-indigo-400 dark:group-hover:border-indigo-500'}`}>
                      {selectedCategory === category && <Check className="h-3.5 w-3.5 text-white" />}
                    </div>
                    <span className={`text-sm ${selectedCategory === category ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white'}`}>{category}</span>
                    <input
                      type="radio"
                      className="hidden"
                      checked={selectedCategory === category}
                      onChange={() => setSelectedCategory(category)}
                    />
                  </label>
                ))}
              </div>
            </div>

            {/* Price Range */}
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Price Range</h3>
              <input
                type="range"
                min="0"
                max="100"
                className="w-full accent-indigo-600"
                value={priceRange[1]}
                onChange={(e) => setPriceRange([0, parseInt(e.target.value)])}
              />
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-2">
                <span>$0</span>
                <span>${priceRange[1]}</span>
              </div>
            </div>

            {/* Format */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Format</h3>
              <div className="space-y-3">
                {FORMATS.map(format => (
                  <label key={format} className="flex items-center cursor-pointer group">
                    <div className="w-5 h-5 rounded border border-gray-300 dark:border-gray-600 flex items-center justify-center mr-3 group-hover:border-indigo-400 dark:group-hover:border-indigo-500">
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white">{format}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {/* Top Bar */}
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 bg-white dark:bg-gray-950 p-4 rounded-xl border border-gray-200 dark:border-gray-800 transition-colors duration-200">
            <div className="mb-4 sm:mb-0">
              {searchQuery ? (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Search results for <span className="font-bold text-gray-900 dark:text-white">"{searchQuery}"</span> ({filteredBooks.length} results)
                </p>
              ) : (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Showing <span className="font-medium text-gray-900 dark:text-white">
                    {filteredBooks.length === 0 ? 0 : (currentPage - 1) * ITEMS_PER_PAGE + 1}-
                    {Math.min(currentPage * ITEMS_PER_PAGE, filteredBooks.length)}
                  </span> of <span className="font-medium text-gray-900 dark:text-white">{filteredBooks.length}</span> results
                </p>
              )}
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400 mr-2">Sort by:</span>
                <div className="relative">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="appearance-none bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5 pr-8 transition-colors duration-200"
                  >
                    <option value="Most Popular">Most Popular</option>
                    <option value="Newest Arrivals">Newest Arrivals</option>
                    <option value="Price: Low to High">Price: Low to High</option>
                    <option value="Price: High to Low">Price: High to Low</option>
                    <option value="Highest Rated">Highest Rated</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-3 h-4 w-4 text-gray-500 dark:text-gray-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Book Grid */}
          {paginatedBooks.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {paginatedBooks.map((book: any) => (
                <Link key={book.id} to={`/book/${book.id}`} className="group flex flex-col bg-white dark:bg-gray-950 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all border border-gray-100 dark:border-gray-800 hover:border-indigo-100 dark:hover:border-gray-700">
                  <div className="aspect-w-2 aspect-h-3 bg-gray-200 dark:bg-gray-800 overflow-hidden relative">
                    <img
                      src={book.image || book.cover_image || `https://picsum.photos/seed/book${book.id}/200/300`}
                      alt={book.title}
                      className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                      referrerPolicy="no-referrer"
                    />
                    {/* Quick Add Button Overlay */}
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white font-medium py-2 px-4 rounded-full shadow-lg hover:bg-indigo-50 dark:hover:bg-gray-800 transform translate-y-4 group-hover:translate-y-0 transition-all">
                        Quick View
                      </button>
                    </div>

                    {/* Wishlist Button */}
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        if (isInWishlist(book.id)) {
                          removeFromWishlist(book.id);
                        } else {
                          addToWishlist(book);
                        }
                      }}
                      className="absolute top-3 right-3 p-2 rounded-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm hover:bg-white dark:hover:bg-gray-900 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-colors shadow-sm z-10"
                    >
                      <Heart className={`h-4 w-4 ${isInWishlist(book.id) ? 'fill-red-500 text-red-500' : ''}`} />
                    </button>
                  </div>
                  <div className="p-4 flex flex-col flex-grow">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{book.category || 'General'}</p>
                      <div className="flex items-center">
                        <Star className="h-3.5 w-3.5 text-yellow-400 fill-current" />
                        <span className="ml-1 text-xs text-gray-600 dark:text-gray-400">{book.rating || '0'}</span>
                      </div>
                    </div>
                    <h3 className="text-base font-bold text-gray-900 dark:text-white mb-1 line-clamp-1">{book.title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">{book.author}</p>
                    <div className="mt-auto flex items-center justify-between">
                      <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">${book.price || '0.00'}</span>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          addToCart({ ...book, format: 'Paperback' });
                        }}
                        className="text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors p-1.5 rounded-full hover:bg-indigo-50 dark:hover:bg-gray-800"
                      >
                        <ShoppingCart className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 bg-white dark:bg-gray-950 rounded-2xl border border-gray-200 dark:border-gray-800">
              <SearchX className="h-16 w-16 text-gray-400 dark:text-gray-600 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No books found</h3>
              <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">
                We couldn't find any books matching your search criteria. Try adjusting your filters or search query.
              </p>
              <button
                onClick={() => {
                  setSelectedCategory("All");
                  setPriceRange([0, 50]);
                  window.history.replaceState(null, '', '/catalog');
                  window.dispatchEvent(new Event('popstate'));
                }}
                className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-12 flex justify-center">
              <nav className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 transition-colors"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>

                {[...Array(totalPages)].map((_, i) => {
                  const page = i + 1;
                  if (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  ) {
                    return (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`w-10 h-10 rounded-lg font-medium flex items-center justify-center transition-colors ${
                          currentPage === page
                            ? 'bg-indigo-600 text-white border border-indigo-600'
                            : 'border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  }
                  if (
                    (page === 2 && currentPage > 3) ||
                    (page === totalPages - 1 && currentPage < totalPages - 2)
                  ) {
                    return <span key={page} className="text-gray-500 dark:text-gray-400 px-1">...</span>;
                  }
                  return null;
                })}

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 transition-colors"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </nav>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
