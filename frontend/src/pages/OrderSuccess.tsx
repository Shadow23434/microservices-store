import { Link } from 'react-router-dom';
import { CheckCircle, Package, Truck, MapPin } from 'lucide-react';
import { useOrders } from '../contexts/OrderContext';

export default function OrderSuccess() {
  const { currentOrder } = useOrders();

  if (!currentOrder) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">No recent order found</h2>
          <Link to="/catalog" className="text-indigo-600 hover:text-indigo-500 font-medium">Continue Shopping</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-950 min-h-screen py-12 transition-colors duration-200">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-sm border border-gray-200 dark:border-gray-800 overflow-hidden transition-colors">
          {/* Header */}
          <div className="bg-indigo-600 dark:bg-indigo-900 px-8 py-12 text-center text-white">
            <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6 backdrop-blur-sm">
              <CheckCircle className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold mb-2">Thank You for Your Order!</h1>
            <p className="text-indigo-100 text-lg">Your order #{currentOrder.id} has been confirmed.</p>
          </div>

          <div className="p-8">
            {/* Tracking Timeline */}
            <div className="mb-12">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Shipment Tracking</h2>
              <div className="relative">
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>
                <div className="space-y-8 relative">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-indigo-600 rounded-full flex items-center justify-center flex-shrink-0 z-10 shadow-md shadow-indigo-200 dark:shadow-indigo-900/50">
                      <CheckCircle className="h-6 w-6 text-white" />
                    </div>
                    <div className="pt-3">
                      <h3 className="font-bold text-gray-900 dark:text-white">Order Placed</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{currentOrder.date}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/50 border-2 border-indigo-600 dark:border-indigo-400 rounded-full flex items-center justify-center flex-shrink-0 z-10">
                      <Package className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div className="pt-3">
                      <h3 className="font-bold text-gray-900 dark:text-white">Processing</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">We are preparing your items.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 opacity-50">
                    <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-full flex items-center justify-center flex-shrink-0 z-10">
                      <Truck className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="pt-3">
                      <h3 className="font-bold text-gray-900 dark:text-white">Shipped</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Pending</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 opacity-50">
                    <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-full flex items-center justify-center flex-shrink-0 z-10">
                      <MapPin className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="pt-3">
                      <h3 className="font-bold text-gray-900 dark:text-white">Delivered</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Estimated: March 20, 2026</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Order Details */}
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-2xl p-6 mb-8 border border-gray-100 dark:border-gray-700">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Order Details</h2>
              <div className="space-y-4">
                {currentOrder.items.map((item) => (
                  <div key={item.id} className="flex gap-4">
                    <img src={item.image} alt={item.title} className="w-12 h-16 object-cover rounded shadow-sm" referrerPolicy="no-referrer" />
                    <div className="flex-1">
                      <h3 className="text-sm font-bold text-gray-900 dark:text-white">{item.title}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Qty: {item.quantity} • {item.format}</p>
                    </div>
                    <div className="font-bold text-gray-900 dark:text-white">${(parseFloat(item.price) * item.quantity).toFixed(2)}</div>
                  </div>
                ))}
              </div>
              <div className="border-t border-gray-200 dark:border-gray-700 mt-6 pt-4 space-y-2">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Subtotal</span>
                  <span>${currentOrder.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Shipping</span>
                  <span>${currentOrder.shipping.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Tax</span>
                  <span>${currentOrder.tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold text-gray-900 dark:text-white pt-2">
                  <span>Total</span>
                  <span className="text-indigo-600 dark:text-indigo-400">${currentOrder.total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/catalog" className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-colors text-center">
                Continue Shopping
              </Link>
              <Link to="/account" className="px-8 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-bold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-center">
                View My Orders
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
