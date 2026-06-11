import React from 'react';
import { BookOpen, Users, Globe } from 'lucide-react';

export default function AboutUs() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 transition-colors duration-200">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">About Store</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          We are passionate about bringing the best stories to readers around the world. Our mission is to foster a love for reading and build a community of e-commerce enthusiasts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-20">
        <div className="text-center">
          <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <BookOpen className="h-8 w-8" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Vast Collection</h3>
          <p className="text-gray-600 dark:text-gray-400">
            From timeless classics to the latest bestsellers, our carefully curated collection has something for every reader.
          </p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Users className="h-8 w-8" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Community First</h3>
          <p className="text-gray-600 dark:text-gray-400">
            We believe in the power of shared stories. Join our reading groups, author events, and vibrant online community.
          </p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Globe className="h-8 w-8" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Global Reach</h3>
          <p className="text-gray-600 dark:text-gray-400">
            We ship worldwide and offer a massive selection of digital formats so you can read anywhere, anytime.
          </p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-950 rounded-3xl p-8 md:p-12 border border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Our Story</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
              Founded in 2020 by a group of avid readers, Store started as a small independent shop with a simple goal: to make great books accessible to everyone.
            </p>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Today, we've grown into a global platform, but our core values remain the same. We still hand-pick our recommendations, support independent authors, and strive to provide the best possible experience for our customers.
            </p>
          </div>
          <div className="relative h-64 sm:h-80 lg:h-full min-h-[300px] rounded-2xl overflow-hidden">
            <img 
              src="https://images.unsplash.com/photo-1507842217343-583bb7270b66?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
              alt="Library interior" 
              className="absolute inset-0 w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
