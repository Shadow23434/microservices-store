import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle2, CreditCard, Truck, ChevronRight, Trash2, Plus, Minus, ShoppingCart, Loader2 } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useOrders } from '../contexts/OrderContext';
import { useAuth } from '../contexts/AuthContext';
import orderService from '../api/orderService';

export default function Checkout() {
  const navigate = useNavigate();
  const { cartItems, cartTotal, updateQuantity, removeFromCart, clearCart } = useCart();
  const { addOrder } = useOrders();
  const { user } = useAuth();
  const [step, setStep] = useState(0); // 0: Cart, 1: Shipping, 2: Payment
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [isPlacingOrder, setIsPlacingOrder] = useState(false);
  
  // Shipping form states
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [shippingAddress, setShippingAddress] = useState(user?.address || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [city, setCity] = useState('');
  const [stateProv, setStateProv] = useState('');
  const [zip, setZip] = useState('');

  const isShippingValid = firstName.trim() !== '' && lastName.trim() !== '' && shippingAddress.trim() !== '' && phone.trim() !== '';

  const subtotal = cartTotal;
  const shipping = 5.99;
  const tax = subtotal * 0.08;
  const total = subtotal + shipping + tax;

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPlacingOrder(true);

    try {
      // Gọi API thật $ể tạo order trong backend
      // Order service tự $ộng tạo Payment và Shipment
      const orderData = {
        customer_id: user?.id || 1,
        shipping_address: shippingAddress || '123 Default St',
        payment_method: paymentMethod,
        items: cartItems.map((item: any) => ({
          product_id: item.id,
          quantity: item.quantity,
          unit_price: item.price,
        })),
      };

      const createdOrder: any = await orderService.createOrder(orderData);

      // Cũng lưu vào OrderContext local state
      addOrder({
        id: createdOrder?.id || `ORD-${Date.now()}`,
        date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
        items: [...cartItems],
        subtotal,
        shipping,
        tax,
        total,
        status: 'Processing' as const
      });
      clearCart();

      if (paymentMethod === 'qr_code') {
        navigate('/scan-to-pay');
      } else if (paymentMethod === 'paypal') {
        navigate('/scan-to-pay?method=paypal');
      } else {
        navigate('/order-success');
      }
    } catch (err) {
      console.error('Failed to place order:', err);
      // Fallback local-only in case API fails
      addOrder({
        id: `ORD-${Date.now()}`,
        date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
        items: [...cartItems],
        subtotal,
        shipping,
        tax,
        total,
        status: 'Processing' as const
      });
      clearCart();

      if (paymentMethod === 'qr_code') {
        navigate('/scan-to-pay');
      } else if (paymentMethod === 'paypal') {
        navigate('/scan-to-pay?method=paypal');
      } else {
        navigate('/order-success');
      }
    } finally {
      setIsPlacingOrder(false);
    }
  };

  if (cartItems.length === 0 && step === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 transition-colors duration-200">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
            <ShoppingCart className="h-12 w-12 text-gray-400 dark:text-gray-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Your cart is empty</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
            Looks like you haven't added any products to your cart yet. Explore our catalog to find your next great read!
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
    <div className="bg-gray-50 dark:bg-gray-950 min-h-screen py-12 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-8">Checkout</h1>

        <div className="flex flex-col lg:flex-row gap-12">
          {/* Main Checkout Form */}
          <div className="w-full lg:w-2/3">
            {/* Progress Steps */}
            {step > 0 && (
              <div className="flex items-center mb-8">
                <div className={`flex items-center ${step >= 1 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400 dark:text-gray-600'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step >= 1 ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30' : 'border-gray-300 dark:border-gray-700'}`}>
                    1
                  </div>
                  <span className="ml-3 font-medium">Shipping</span>
                </div>
                <div className={`flex-1 h-0.5 mx-4 ${step >= 2 ? 'bg-indigo-600 dark:bg-indigo-400' : 'bg-gray-300 dark:bg-gray-700'}`}></div>
                <div className={`flex items-center ${step >= 2 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400 dark:text-gray-600'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step >= 2 ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30' : 'border-gray-300 dark:border-gray-700'}`}>
                    2
                  </div>
                  <span className="ml-3 font-medium">Payment</span>
                </div>
              </div>
            )}

            <form onSubmit={handlePlaceOrder}>
              {step === 0 && (
                <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 transition-colors">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                    <ShoppingCart className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> Shopping Cart
                  </h2>
                  <div className="space-y-6">
                    {cartItems.map((item) => (
                      <div key={item.id} className="flex flex-col sm:flex-row gap-4 py-4 border-b border-gray-100 dark:border-gray-800 last:border-0">
                        <img src={item.image} alt={item.title} className="w-24 h-36 object-cover rounded shadow-sm" referrerPolicy="no-referrer" />
                        <div className="flex-1 flex flex-col">
                          <div className="flex justify-between items-start">
                            <div>
                              <h3 className="text-lg font-bold text-gray-900 dark:text-white">{item.title}</h3>
                              <p className="text-sm text-gray-500 dark:text-gray-400">{item.author}</p>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{item.format}</p>
                            </div>
                            <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">${parseFloat(item.price).toFixed(2)}</span>
                          </div>
                          <div className="mt-auto flex items-center justify-between pt-4">
                            <div className="flex items-center border border-gray-300 dark:border-gray-700 rounded-lg">
                              <button 
                                type="button"
                                onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                              >
                                <Minus className="h-4 w-4" />
                              </button>
                              <span className="w-10 text-center font-medium text-gray-900 dark:text-white">{item.quantity}</span>
                              <button 
                                type="button"
                                onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                              >
                                <Plus className="h-4 w-4" />
                              </button>
                            </div>
                            <button 
                              type="button"
                              onClick={() => removeFromCart(item.id)}
                              className="text-red-500 hover:text-red-700 transition-colors flex items-center gap-1 text-sm font-medium"
                            >
                              <Trash2 className="h-4 w-4" /> Remove
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-8 flex justify-end">
                    <button 
                      type="button" 
                      onClick={() => setStep(1)}
                      className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-indigo-700 transition-colors flex items-center gap-2"
                    >
                      Proceed to Checkout <ChevronRight className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              )}

              {step === 1 && (
                <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 transition-colors">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                    <Truck className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> Shipping Address
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        First Name <span className="text-red-500">*</span>
                      </label>
                      <input 
                        type="text" 
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                        required 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Last Name <span className="text-red-500">*</span>
                      </label>
                      <input 
                        type="text" 
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                        required 
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Address <span className="text-red-500">*</span>
                      </label>
                      <input 
                        type="text" 
                        value={shippingAddress}
                        onChange={(e) => setShippingAddress(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                        required 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">City</label>
                      <input 
                        type="text" 
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">State / Province</label>
                      <input 
                        type="text" 
                        value={stateProv}
                        onChange={(e) => setStateProv(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ZIP / Postal Code</label>
                      <input 
                        type="text" 
                        value={zip}
                        onChange={(e) => setZip(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Phone Number <span className="text-red-500">*</span>
                      </label>
                      <input 
                        type="tel" 
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500" 
                        required 
                      />
                    </div>
                  </div>
                  <div className="flex justify-between items-center mt-6">
                    <button 
                      type="button" 
                      onClick={() => setStep(0)}
                      className="text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-800 dark:hover:text-indigo-300"
                    >
                      Back to Cart
                    </button>
                    <button 
                      type="button" 
                      onClick={() => {
                        if (isShippingValid) setStep(2);
                      }}
                      disabled={!isShippingValid}
                      className={`px-8 py-3 rounded-lg font-bold transition-colors flex items-center gap-2 ${
                        isShippingValid 
                          ? 'bg-indigo-600 text-white hover:bg-indigo-700' 
                          : 'bg-indigo-300 text-white cursor-not-allowed dark:bg-indigo-900/50'
                      }`}
                    >
                      Continue to Payment <ChevronRight className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 transition-colors">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                    <CreditCard className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> Payment Method
                  </h2>
                  
                  <div className="space-y-4 mb-8">
                    <label className={`flex items-center p-4 border rounded-xl cursor-pointer transition-colors ${paymentMethod === 'credit_card' ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30' : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'}`}>
                      <input 
                        type="radio" 
                        name="payment" 
                        value="credit_card" 
                        checked={paymentMethod === 'credit_card'}
                        onChange={() => setPaymentMethod('credit_card')}
                        className="h-5 w-5 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-3 font-medium text-gray-900 dark:text-white">Credit Card</span>
                      <div className="ml-auto flex gap-2">
                        <div className="w-10 h-6 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        <div className="w-10 h-6 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      </div>
                    </label>
                    <label className={`flex items-center p-4 border rounded-xl cursor-pointer transition-colors ${paymentMethod === 'paypal' ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30' : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'}`}>
                      <input 
                        type="radio" 
                        name="payment" 
                        value="paypal" 
                        checked={paymentMethod === 'paypal'}
                        onChange={() => setPaymentMethod('paypal')}
                        className="h-5 w-5 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-3 font-medium text-gray-900 dark:text-white">PayPal</span>
                    </label>
                    <label className={`flex items-center p-4 border rounded-xl cursor-pointer transition-colors ${paymentMethod === 'qr_code' ? 'border-indigo-600 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30' : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'}`}>
                      <input 
                        type="radio" 
                        name="payment" 
                        value="qr_code" 
                        checked={paymentMethod === 'qr_code'}
                        onChange={() => setPaymentMethod('qr_code')}
                        className="h-5 w-5 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-3 font-medium text-gray-900 dark:text-white">Scan QR Code to Pay</span>
                    </label>
                  </div>

                  {paymentMethod === 'credit_card' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                      <div className="sm:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Card Number</label>
                        <input type="text" placeholder="0000 0000 0000 0000" className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500 placeholder-gray-400 dark:placeholder-gray-500" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Expiration Date</label>
                        <input type="text" placeholder="MM/YY" className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500 placeholder-gray-400 dark:placeholder-gray-500" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">CVC</label>
                        <input type="text" placeholder="123" className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2.5 text-gray-900 dark:text-white focus:ring-indigo-500 focus:border-indigo-500 placeholder-gray-400 dark:placeholder-gray-500" />
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-center">
                    <button 
                      type="button" 
                      onClick={() => setStep(1)}
                      className="text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-800 dark:hover:text-indigo-300"
                    >
                      Back to Shipping
                    </button>
                    <button 
                      type="submit" 
                      className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-indigo-700 transition-colors flex items-center gap-2"
                    >
                      <CheckCircle2 className="h-5 w-5" /> Place Order
                    </button>
                  </div>
                </div>
              )}
            </form>
          </div>

          {/* Order Summary */}
          <div className="w-full lg:w-1/3">
            <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 sticky top-24 transition-colors">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Order Summary</h2>
              
              <div className="space-y-4 mb-6">
                {cartItems.map((item) => (
                  <div key={item.id} className="flex gap-4">
                    <img src={item.image} alt={item.title} className="w-16 h-24 object-cover rounded shadow-sm" referrerPolicy="no-referrer" />
                    <div className="flex-1">
                      <h3 className="text-sm font-bold text-gray-900 dark:text-white line-clamp-2">{item.title}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{item.author}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Qty: {item.quantity} • {item.format}</p>
                      <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400 mt-1">${(parseFloat(item.price) * item.quantity).toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t border-gray-200 dark:border-gray-800 pt-4 space-y-3">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Subtotal</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Shipping</span>
                  <span>${shipping.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Estimated Tax</span>
                  <span>${tax.toFixed(2)}</span>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-800 pt-3 flex justify-between items-center">
                  <span className="text-lg font-bold text-gray-900 dark:text-white">Total</span>
                  <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">${total.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
