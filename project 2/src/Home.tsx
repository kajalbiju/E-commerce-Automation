import React from 'react';
import { ProductCard } from '../components/ProductCard';
import { Product } from '../types';

const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Logitech G304 Wireless Gaming Mouse',
    price: 70.00,
    description: 'High-performance wireless gaming mouse with HERO sensor',
    image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Black',
    weight: '99g',
    subcategory: 'Gaming Peripherals'
  },
  {
    id: '2',
    name: 'Mechanical Gaming Keyboard',
    price: 129.99,
    description: 'RGB mechanical keyboard with Cherry MX switches for the ultimate gaming experience',
    image: 'https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Black/RGB',
    subcategory: 'Gaming Peripherals'
  },
  {
    id: '3',
    name: 'Pro Gaming Headset',
    price: 159.99,
    description: '7.1 surround sound gaming headset with noise-canceling microphone',
    image: 'https://images.unsplash.com/photo-1599669454699-248893623440?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Black/Red',
    weight: '350g',
    subcategory: 'Audio Equipment'
  },
  {
    id: '4',
    name: 'Ultra-wide Gaming Monitor',
    price: 499.99,
    description: '34-inch curved ultra-wide monitor with 144Hz refresh rate and 1ms response time',
    image: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Black',
    size: '34"',
    subcategory: 'Monitors'
  },
  {
    id: '5',
    name: 'Gaming Mouse Pad XL',
    price: 29.99,
    description: 'Extended gaming mouse pad with stitched edges and smooth surface',
    image: 'https://images.unsplash.com/photo-1603575448878-868a20723f5d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Black',
    size: '900x400mm',
    subcategory: 'Gaming Accessories'
  },
  {
    id: '6',
    name: 'Gaming Chair',
    price: 299.99,
    description: 'Ergonomic gaming chair with lumbar support and adjustable armrests',
    image: 'https://images.unsplash.com/photo-1598550476439-6847785fcea6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Black/Blue',
    weight: '20kg',
    subcategory: 'Gaming Furniture'
  },
  {
    id: '7',
    name: 'Streaming Microphone',
    price: 129.99,
    description: 'USB condenser microphone perfect for streaming and podcasting',
    image: 'https://images.unsplash.com/photo-1583595366761-5f9a3cb88177?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'Silver',
    weight: '1.2kg',
    subcategory: 'Streaming Equipment'
  },
  {
    id: '8',
    name: 'RGB LED Strip',
    price: 39.99,
    description: 'Customizable RGB LED strip for gaming setup ambient lighting',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'RGB',
    size: '5m',
    subcategory: 'Gaming Accessories'
  },
{
    id: '9',
    name: 'RGB LED Strip',
    price: 39.99,
    description: 'Customizable RGB LED strip for gaming setup ambient lighting',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
    color: 'RGB',
    size: '5m',
    subcategory: 'Gaming Accessories'
  },

];

export const Home: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Featured Products</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {mockProducts.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};