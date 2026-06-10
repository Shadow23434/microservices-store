import { Link, useNavigate, useLocation } from 'react-router-dom';
import { QrCode, BookOpen, Bell, UserCircle, ScanLine, Clock, Download, Lock, ShieldCheck } from 'lucide-react';
import { useOrders } from '../contexts/OrderContext';
import { useState, useEffect } from 'react';

export default function ScanToPay() {
  const { currentOrder } = useOrders();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPaypal, setShowPaypal] = useState(false);

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    if (searchParams.get('method') === 'paypal') {
      setShowPaypal(true);
    }
  }, [location]);

  if (!currentOrder) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">No pending order found</h2>
          <Link to="/cart" className="text-indigo-600 hover:text-indigo-500 font-medium">Return to Cart</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen flex flex-col bg-[#f6f6f8] dark:bg-[#14131f] font-sans text-slate-900 dark:text-slate-100 overflow-x-hidden">
      {/* Background Content (Blurred/Dimmed) */}
      <div className={`layout-container flex h-full grow flex-col transition-all duration-300 ${showPaypal ? 'filter blur-[2px] pointer-events-none select-none' : ''}`}>
        
        {/* Top Navigation Bar */}
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-slate-800 px-6 md:px-20 py-4 bg-white dark:bg-[#14131f]">
          <div className="flex items-center gap-4 text-slate-900 dark:text-slate-100">
            <div className="h-8 w-8 text-[#d36d24] flex items-center justify-center">
              <BookOpen className="h-8 w-8" />
            </div>
            <h2 className="text-xl font-bold leading-tight tracking-[-0.015em]">LuminiaBooks</h2>
          </div>
          <div className="flex gap-3">
            <button className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 transition-colors hover:bg-slate-200 dark:hover:bg-slate-700">
              <Bell className="h-6 w-6" />
            </button>
            <button className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 transition-colors hover:bg-slate-200 dark:hover:bg-slate-700">
              <UserCircle className="h-6 w-6" />
            </button>
          </div>
        </header>

        <main className="flex flex-1 justify-center py-10 px-4 md:px-0">
          <div className="layout-content-container flex flex-col max-w-[520px] w-full gap-8 bg-white dark:bg-slate-900 p-8 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
            <div className="flex flex-col items-center text-center gap-2">
              <h2 className="text-slate-900 dark:text-slate-100 text-3xl font-bold leading-tight">Scan to Pay</h2>
              <p className="text-slate-600 dark:text-slate-400 text-base">Scan this QR code to complete your payment securely.</p>
            </div>

            {/* QR Code Container */}
            <div className="flex flex-col items-center justify-center gap-6">
              <div className="relative p-6 bg-white rounded-2xl border-2 border-[#d36d24]/20 shadow-inner">
                <QrCode className="object-cover w-48 h-48 sm:w-64 sm:h-64 aspect-square text-black" />
                
                {/* Corner Accents */}
                <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-[#d36d24] rounded-tl-lg"></div>
                <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-[#d36d24] rounded-tr-lg"></div>
                <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-[#d36d24] rounded-bl-lg"></div>
                <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-[#d36d24] rounded-br-lg"></div>
              </div>

              <div className="flex items-center gap-2 text-[#d36d24] font-semibold">
                <ScanLine className="h-5 w-5 animate-pulse" />
                <span>Waiting for scan...</span>
              </div>
              <div className="flex items-center gap-2 text-[#d36d24] font-bold bg-[#d36d24]/5 px-4 py-2 rounded-full border border-[#d36d24]/10">
                <Clock className="h-5 w-5" />
                <span>QR code expires in <span className="tabular-nums">04:59</span></span>
              </div>
            </div>

            {/* Payment Summary Card */}
            <div className="flex flex-col gap-4 rounded-xl p-6 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <div className="flex justify-between items-center">
                <p className="text-slate-600 dark:text-slate-400 text-base font-medium">Order Number</p>
                <p className="text-slate-900 dark:text-slate-100 font-bold">{currentOrder.id}</p>
              </div>
              <div className="h-px bg-slate-200 dark:bg-slate-700 w-full"></div>
              <div className="flex justify-between items-center">
                <p className="text-slate-600 dark:text-slate-400 text-lg font-medium">Total Amount</p>
                <p className="text-slate-900 dark:text-slate-100 tracking-tight text-3xl font-bold">${currentOrder.total.toFixed(2)}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-3">
              <button 
                onClick={() => navigate('/order-success')}
                className="w-full flex items-center justify-center rounded-lg h-12 bg-[#d36d24] text-white gap-2 text-base font-bold leading-normal transition-opacity hover:opacity-90"
              >
                <Download className="h-5 w-5" /> Save QR Code
              </button>
              <button 
                onClick={() => navigate('/checkout')}
                className="w-full flex items-center justify-center rounded-lg h-12 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 gap-2 text-base font-bold leading-normal transition-colors hover:bg-slate-200 dark:hover:bg-slate-700"
              >
                Cancel Payment
              </button>
            </div>

            <div className="flex items-center justify-center gap-4 pt-2">
              <div className="flex items-center gap-1 text-slate-400">
                <Lock className="h-4 w-4" />
                <span className="text-xs uppercase tracking-widest font-bold">Encrypted</span>
              </div>
              <div className="h-1 w-1 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
              <div className="flex items-center gap-1 text-slate-400">
                <ShieldCheck className="h-4 w-4" />
                <span className="text-xs uppercase tracking-widest font-bold">Verified</span>
              </div>
            </div>
          </div>
        </main>

        {/* Footer Section */}
        <footer className="flex flex-col gap-6 border-t border-solid border-slate-200 dark:border-slate-800 px-6 md:px-20 py-10 bg-white dark:bg-[#14131f]">
          <div className="flex flex-wrap justify-between gap-8 max-w-7xl mx-auto w-full">
            <div className="flex flex-col gap-4 min-w-[200px]">
              <div className="flex items-center gap-2 text-slate-900 dark:text-slate-100">
                <BookOpen className="h-6 w-6 text-[#d36d24]" />
                <span className="text-lg font-bold">LuminiaBooks</span>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-sm max-w-xs">
                Elevating your reading experience with curated collections and seamless digital payments.
              </p>
            </div>
            <div className="flex gap-12">
              <div className="flex flex-col gap-3">
                <h4 className="text-slate-900 dark:text-slate-100 font-bold text-sm uppercase tracking-wider">Support</h4>
                <a className="text-slate-500 dark:text-slate-400 hover:text-[#d36d24] transition-colors text-sm" href="#">Help Center</a>
                <a className="text-slate-500 dark:text-slate-400 hover:text-[#d36d24] transition-colors text-sm" href="#">Terms of Service</a>
              </div>
              <div className="flex flex-col gap-3">
                <h4 className="text-slate-900 dark:text-slate-100 font-bold text-sm uppercase tracking-wider">Account</h4>
                <a className="text-slate-500 dark:text-slate-400 hover:text-[#d36d24] transition-colors text-sm" href="#">My Library</a>
                <a className="text-slate-500 dark:text-slate-400 hover:text-[#d36d24] transition-colors text-sm" href="#">Transaction History</a>
              </div>
            </div>
          </div>
          <div className="pt-6 border-t border-slate-100 dark:border-slate-800 text-center">
            <p className="text-slate-400 text-xs">© 2024 LuminiaBooks. All rights reserved.</p>
          </div>
        </footer>
      </div>

      {/* Dimmed Overlay & Modal */}
      {showPaypal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-40 flex items-center justify-center p-4">
          {/* PayPal Modal */}
          <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-2xl shadow-2xl overflow-hidden z-50 animate-in fade-in zoom-in duration-300">
            <div className="p-8 flex flex-col items-center text-center">
              {/* PayPal Logo Placeholder */}
              <div className="mb-6">
                <div className="flex items-center gap-1 text-[#003087] dark:text-blue-400 font-bold text-3xl italic font-serif">
                  <span className="text-[#003087]">Pay</span><span className="text-[#009cde]">Pal</span>
                </div>
              </div>

              <div className="mb-8">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Redirecting to PayPal...</h2>
                <p className="text-slate-600 dark:text-slate-400">
                  Please log in to your account to authorize the payment of <span className="font-semibold text-slate-900 dark:text-white">${currentOrder.total.toFixed(2)}</span>.
                </p>
              </div>

              {/* Progress Indicator */}
              <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mb-8">
                <div className="bg-[#d36d24] h-full w-2/3 rounded-full animate-pulse"></div>
              </div>

              <div className="flex flex-col w-full gap-3">
                <button 
                  onClick={() => navigate('/order-success')}
                  className="w-full text-white font-bold py-3.5 rounded-full flex items-center justify-center gap-2 transition-colors bg-[#d36d24] hover:brightness-95"
                >
                  <span>Login with PayPal</span>
                </button>
                <button 
                  onClick={() => {
                    setShowPaypal(false);
                    navigate('/checkout'); // go back to checkout when cancel paypal popup
                  }}
                  className="w-full bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 font-medium py-3 rounded-full transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 px-8 py-4 flex justify-center items-center gap-4 border-t border-slate-100 dark:border-slate-800">
              <Lock className="text-slate-400 h-4 w-4" />
              <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-widest font-semibold">Secure Encryption</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
