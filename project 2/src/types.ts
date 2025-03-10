export interface Product {
  id: string;
  name: string;
  color?: string;
  price: number;
  size?: string;
  weight?: string;
  description: string;
  subcategory?: string;
  image: string;
}

export interface CartItem extends Product {
  quantity: number;
}