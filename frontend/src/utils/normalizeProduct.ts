import { Product } from '../types';

// Normalize product data for display in wishlist/cart
export function normalizeProduct(product: any): Product {
  const detail = product.detail || {};
  const productType = (product.product_type || '').toLowerCase();

  // Get title/name
  const name = product.name || product.title || 'Unknown Product';

  // Get image
  const image = product.image || product.image_url || product.cover_image ||
    `https://picsum.photos/seed/product${product.id}/400/600`;

  // Get author/brand based on product type
  let author = '';
  if (productType === 'book') {
    author = detail.author || product.author || '';
  } else {
    author = detail.brand || product.brand || '';
  }

  // Get category
  const category = product.category || product.product_type || 'General';

  // Get price
  const price = product.price || '0.00';

  // Get stock
  const stock = product.stock || product.stock_quantity || 15;

  return {
    id: product.id,
    name,
    title: name, // For backward compatibility
    product_type: productType as any,
    price: String(price),
    stock,
    description: product.description || '',
    category_id: product.category_id,
    image_url: image,
    image: image, // For backward compatibility
    sku: product.sku || '',
    is_active: product.is_active ?? true,
    created_at: product.created_at || '',
    updated_at: product.updated_at || '',
    detail: product.detail || null,
    // Additional fields for display
    author,
    category,
  } as Product;
}