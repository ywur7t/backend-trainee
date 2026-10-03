const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8004";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    const text = await response.text();
    let message = `HTTP ${response.status}`;
    try {
      const data = JSON.parse(text);
      message = data.detail || data.message || message;
    } catch {
      if (text) message = text;
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export type Restaurant = {
  id: number;
  external_id?: string;
  name: string;
  description?: string | null;
  is_open?: boolean;
};

export type Category = { id: number; name: string; sort_order: number };

export type MenuItem = {
  id: number;
  external_id?: string;
  name: string;
  description?: string | null;
  price: number | string;
  is_available: boolean;
  category_id?: number;
};

export type MenuResponse = {
  restaurant_id: number;
  restaurant_name: string;
  categories: Category[];
  items: MenuItem[];
};

export type Order = {
  id: number;
  status: string | { name: string };
  total_price: number | string;
  restaurant?: { id: number; name: string };
  delivery_address?: {
    city: string;
    street: string;
    house: string;
    apartment?: string | null;
    floor?: string | null;
  };
};

export function getRestaurants() {
  return request<Restaurant[]>("/api/v1/restaurants");
}

export function getRestaurantMenu(id: number) {
  return request<MenuResponse>(`/api/v1/restaurants/${id}/menu`);
}

export function createOrder(data: {
  customer_id: number;
  restaurant_id: number;
  address_id: number;
  delivery_type_id: number;
  items: { menu_item_id: number; quantity: number }[];
}) {
  return request<Order>("/api/v1/orders", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getOrder(id: number) {
  return request<Order>(`/api/v1/orders/${id}`);
}
