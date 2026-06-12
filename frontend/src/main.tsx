import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { WishlistProvider } from './contexts/WishlistContext';
import { CartProvider } from './contexts/CartContext';
import { OrderProvider } from './contexts/OrderContext';
import { ReviewProvider } from './contexts/ReviewContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Home from './pages/Home';
import Catalog from './pages/Catalog';
import ProductDetail from './pages/ProductDetail';
import Checkout from './pages/Checkout';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import OrderSuccess from './pages/OrderSuccess';
import Account from './pages/Account';
import ScanToPay from './pages/ScanToPay';
import AboutUs from './pages/AboutUs';
import Contact from './pages/Contact';
import Wishlist from './pages/Wishlist';
import { Analytics } from '@vercel/analytics/react';
import './index.css';

const root = createRoot(document.getElementById('root')!);

root.render(
  <React.StrictMode>
    <Analytics />
    <AuthProvider>
      <ThemeProvider defaultTheme="light">
        <OrderProvider>
          <ReviewProvider>
            <CartProvider>
              <WishlistProvider>
                <BrowserRouter>
                  <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<SignUp />} />
                    
                    <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                      <Route index element={<Home />} />
                      <Route path="catalog" element={<Catalog />} />
                      <Route path="product/:id" element={<ProductDetail />} />
                      <Route path="cart" element={<Checkout />} />
                      <Route path="order-success" element={<OrderSuccess />} />
                      <Route path="account" element={<Account />} />
                      <Route path="scan-to-pay" element={<ScanToPay />} />
                      <Route path="about" element={<AboutUs />} />
                      <Route path="contact" element={<Contact />} />
                      <Route path="wishlist" element={<Wishlist />} />
                    </Route>
                  </Routes>
                </BrowserRouter>
              </WishlistProvider>
            </CartProvider>
          </ReviewProvider>
        </OrderProvider>
      </ThemeProvider>
    </AuthProvider>
  </React.StrictMode>
);
