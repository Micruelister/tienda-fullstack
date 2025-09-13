// =================================================================
// FILE: CartContext.jsx (FINAL, STABLE & OPTIMIZED VERSION)
// PURPOSE: Manages the global state for the shopping cart.
// =================================================================

import { createContext, useState, useContext, useMemo, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext.jsx';
import { toast } from 'react-toastify';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();

  const [cartItems, setCartItems] = useState(() => {
    const storedCart = localStorage.getItem('cartItems');
    try {
      return storedCart ? JSON.parse(storedCart) : [];
    } catch (error) {
      console.error("Failed to parse cart from localStorage", error);
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem('cartItems', JSON.stringify(cartItems));
  }, [cartItems]);

  useEffect(() => {
    if (!user) {
      setCartItems([]);
    }
  }, [user]);

  // --- CART MANAGEMENT FUNCTIONS (STABILIZED WITH useCallback) ---

  // useCallback memoizes the function itself, so it isn't recreated on every render.
  // This is crucial for performance and preventing infinite loops in dependent useEffects.
  const addToCart = useCallback((product) => {
    if (!product || !product.name) {
      console.error("addToCart was called with an invalid product object:", product);
      toast.error("An unknown item was added to the cart.");
      return;
    }

    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.id === product.id);
      
      if (existingItem) {
        if (existingItem.quantity >= product.stock) {
          toast.warn(`Only ${product.stock} units of "${product.name}" are in stock.`);
          return prevItems; // Return previous items without change
        }
        return prevItems.map(item =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      if (product.stock < 1) {
        toast.warn(`"${product.name}" is out of stock.`);
        return prevItems;
      }
      return [...prevItems, { ...product, quantity: 1 }];
    });
    
    toast.success(`${product.name} has been added to the cart!`);
  }, []); // Empty dependency array means this function will never change.

  const removeFromCart = useCallback((productId) => {
    setCartItems(prevItems => prevItems.filter(item => item.id !== productId));
    toast.info("Item removed from cart.");
  }, []);

  const updateQuantity = useCallback((productId, newQuantity) => {
    setCartItems(prevItems => {
      const itemToUpdate = prevItems.find(item => item.id === productId);
      if (!itemToUpdate) return prevItems;

      if (newQuantity > itemToUpdate.stock) {
        toast.warn(`Only ${itemToUpdate.stock} of "${itemToUpdate.name}" in stock.`);
        return prevItems; // Return previous items without change
      }

      if (newQuantity < 1) {
        // Instead of calling removeFromCart directly, we integrate its logic
        return prevItems.filter(item => item.id !== productId);
      }
      
      return prevItems.map(item =>
        item.id === productId ? { ...item, quantity: newQuantity } : item
      );
    });
  }, []);

  const clearCart = useCallback(() => {
    setCartItems([]);
    toast.info("Cart has been cleared.");
  }, []);

  const value = useMemo(
    () => ({
      cartItems,
      addToCart,
      removeFromCart,
      updateQuantity,
      clearCart,
    }),
    [cartItems, addToCart, removeFromCart, updateQuantity, clearCart]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}