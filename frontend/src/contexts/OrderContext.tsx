import React, { createContext, useContext, useState, useEffect } from 'react';
import { CartItem } from '../types';

export interface Order {
  id: string;
  date: string;
  items: CartItem[];
  subtotal: number;
  shipping: number;
  tax: number;
  total: number;
  status: 'Processing' | 'Shipped' | 'Delivered';
}

interface OrderContextType {
  orders: Order[];
  addOrder: (order: Order) => void;
  currentOrder: Order | null;
  setCurrentOrder: (order: Order | null) => void;
}

const OrderContext = createContext<OrderContextType | undefined>(undefined);

export function OrderProvider({ children }: { children: React.ReactNode }) {
  const [orders, setOrders] = useState<Order[]>(() => {
    const saved = localStorage.getItem('orders');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [currentOrder, setCurrentOrder] = useState<Order | null>(() => {
    const saved = localStorage.getItem('currentOrder');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    localStorage.setItem('orders', JSON.stringify(orders));
  }, [orders]);

  useEffect(() => {
    if (currentOrder) {
      localStorage.setItem('currentOrder', JSON.stringify(currentOrder));
    } else {
      localStorage.removeItem('currentOrder');
    }
  }, [currentOrder]);

  const addOrder = (order: Order) => {
    setOrders((prev) => [order, ...prev]);
    setCurrentOrder(order);
  };

  return (
    <OrderContext.Provider value={{ orders, addOrder, currentOrder, setCurrentOrder }}>
      {children}
    </OrderContext.Provider>
  );
}

export function useOrders() {
  const context = useContext(OrderContext);
  if (context === undefined) {
    throw new Error('useOrders must be used within an OrderProvider');
  }
  return context;
}
