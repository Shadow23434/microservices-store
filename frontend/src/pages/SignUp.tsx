import { Link, useNavigate } from 'react-router-dom';
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import customerService from '../api/customerService';
import Logo from '../components/Logo';
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function SignUp() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }

    setIsLoading(true);
    try {
      // Gọi API tạo customer mới
      const newCustomer: any = await customerService.createCustomer({
        name: fullName,
        email,
        phone: phone || '',
        address: address || '',
      });

      const names = fullName.trim().split(' ');
      // Đăng nhập ngay sau khi tạo xong, lưu customer_id
      login({
        id: newCustomer.id,
        firstName: names[0] || fullName,
        lastName: names.slice(1).join(' ') || '',
        email: newCustomer.email || email,
        phone: newCustomer.phone || phone,
        address: newCustomer.address || address,
      });
      navigate('/');
    } catch (err: any) {
      console.error('Register error:', err);
      const errMsg = err?.response?.data;
      if (errMsg?.email) {
        setError('Email này $ã $ược $ăng ký. Vui lòng dùng email khác hoặc $ăng nhập.');
      } else {
        setError('Đăng ký thất bại. Vui lòng kiểm tra kết nối và thử lại.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#fdf8f4] dark:bg-[#1a120b] font-sans text-slate-900 dark:text-slate-100 min-h-screen flex flex-col overflow-x-hidden">
      <div className="layout-container flex h-full grow flex-col">
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-[#d36d24]/10 px-6 py-4 lg:px-20 bg-white dark:bg-[#1a120b]/50 backdrop-blur-md sticky top-0 z-50">
          <Link to="/" className="flex items-center gap-2 text-[#d36d24]">
             <Logo className="w-8 h-8 text-[#d36d24] fill-current" />
             <span className="font-bold text-xl text-gray-900 dark:text-slate-100">Store</span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <span className="text-sm text-slate-500 dark:text-slate-400">Already have an account?</span>
            <Link to="/login" className="text-sm font-semibold text-[#d36d24] hover:underline">
              Log in
            </Link>
          </div>
        </header>

        <main className="flex flex-1 items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-[1100px] grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="hidden lg:flex flex-col gap-8">
              <div className="relative h-[500px] w-full rounded-2xl overflow-hidden shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-tr from-[#d36d24]/40 to-transparent z-10"></div>
                <img
                  className="absolute inset-0 w-full h-full object-cover"
                  alt="A cozy sunlit library with wooden shelves filled with books"
                  src="https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=2190&auto=format&fit=crop"
                />
                <div className="absolute bottom-0 left-0 p-8 z-20 text-white">
                  <h3 className="text-3xl font-bold mb-2">Illuminate Your Mind</h3>
                  <p className="text-white/90 text-lg">Join our community of book lovers and discover your next favorite story.</p>
                </div>
              </div>
              <div className="flex items-center gap-6 px-4">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Trusted by <span className="font-bold text-slate-900 dark:text-slate-100">10,000+</span> readers worldwide
                </p>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-900/50 p-8 lg:p-10 rounded-2xl shadow-xl border border-[#d36d24]/10">
              <div className="mb-8">
                <h1 className="text-3xl font-black text-slate-900 dark:text-white leading-tight mb-2">Create Account</h1>
                <p className="text-slate-500 dark:text-slate-400">Join Store today and start your reading journey.</p>
              </div>

              {error && (
                <div className="mb-4 flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400">
                  <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">{error}</p>
                </div>
              )}

              <form className="space-y-5" onSubmit={handleSignUp}>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Full Name</label>
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Enter your full name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                      className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg py-3 px-4 text-slate-900 dark:text-white focus:ring-2 focus:ring-[#d36d24] focus:border-transparent transition-all outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Email Address</label>
                  <div className="relative">
                    <input
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg py-3 px-4 text-slate-900 dark:text-white focus:ring-2 focus:ring-[#d36d24] focus:border-transparent transition-all outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Phone Number <span className="text-slate-400 font-normal">(optional)</span></label>
                  <input
                    type="tel"
                    placeholder="Your phone number"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg py-3 px-4 text-slate-900 dark:text-white focus:ring-2 focus:ring-[#d36d24] focus:border-transparent transition-all outline-none"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Password</label>
                    <div className="relative">
                      <input
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg py-3 pl-4 pr-10 text-slate-900 dark:text-white focus:ring-2 focus:ring-[#d36d24] focus:border-transparent transition-all outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-[#d36d24]"
                      >
                         {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Confirm Password</label>
                    <div className="relative">
                      <input
                        type={showConfirmPassword ? "text" : "password"}
                        placeholder="Confirm your password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg py-3 pl-4 pr-10 text-slate-900 dark:text-white focus:ring-2 focus:ring-[#d36d24] focus:border-transparent transition-all outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-[#d36d24]"
                      >
                        {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3 py-2">
                  <input
                    id="terms"
                    type="checkbox"
                    className="mt-1 h-4 w-4 rounded border-slate-300 text-[#d36d24] focus:ring-[#d36d24] transition-all accent-[#d36d24] cursor-pointer"
                  />
                  <label htmlFor="terms" className="text-sm text-slate-600 dark:text-slate-400 cursor-pointer">
                    I agree to the <a href="#" className="text-[#d36d24] hover:underline font-medium">Terms of Service</a> and <a href="#" className="text-[#d36d24] hover:underline font-medium">Privacy Policy</a>.
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-[#d36d24] hover:bg-[#d36d24]/90 text-white font-bold py-4 rounded-xl shadow-lg shadow-[#d36d24]/20 transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Đang $ăng ký...
                    </span>
                  ) : 'Create Account'}
                </button>

                <p className="text-center text-sm text-slate-500 dark:text-slate-400 pt-4 md:hidden">
                  Already have an account? <Link to="/login" className="text-[#d36d24] font-bold hover:underline">Log in</Link>
                </p>
              </form>
            </div>
          </div>
        </main>

        <footer className="px-6 py-8 text-center text-slate-400 text-xs">
          <p>2026 Store. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}
