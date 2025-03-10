import React, { useEffect, useState } from 'react';
import { ProductCard } from '../components/ProductCard';
import { Product } from '../types';
import axios from 'axios';

export const Home: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch product data from the API
  const fetchProducts = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/posts');

      // Transform API data to ensure `price` is a number or null if not specified
      const apiProducts: Product[] = response.data.map((item: any) => ({
        id: item.id,
        name: item.name,
        price: typeof item.price === "number" ? item.price : 0,  // Set price as number or null
        description: item.description,
        image: item.image || 'https://via.placeholder.com/150',
        color: item.color || "Not specified",
        weight: item.weight || "Not specified",
        subcategory: item.subcategory || "Uncategorized",
      }));

      setProducts(apiProducts);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching products:", err);
      setError("Failed to load products.");
      setLoading(false);
    }
  };

  // Fetch products on component mount
  useEffect(() => {
    fetchProducts();
  }, []);

  // Loading and error states
  if (loading) return <p>Loading products...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Featured Products</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};
