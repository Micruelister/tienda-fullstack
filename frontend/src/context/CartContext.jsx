// =================================================================
// FILE: CartContext.jsx (FINAL POLISHED VERSION)
// =================================================================

import { createContext, useState, useContext, useMemo, useEffect } from 'react';
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

  // --- CART MANAGEMENT FUNCTIONS ---

  const addToCart = (product) => {
    if (!product || !product.name) {
      console.error("addToCart was called with an invalid product object:", product);
      toast.error("An unknown item was added to the cart.");
      return;
    }

    const existingItem = cartItems.find(item => item.id === product.id);
    const quantityInCart = existingItem ? existingItem.quantity : 0;

    if (quantityInCart >= product.stock) {
      toast.warn(`Only ${product.stock} units of "${product.name}" are in stock.`);
      return;
    }

    if (existingItem) {
      setCartItems(cartItems.map(item =>
        item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
      ));
    } else {
      setCartItems([...cartItems, { ...product, quantity: 1 }]);
    }
    
    // Final version of the success toast, without extra quotes
    toast.success(`${product.name} has been added to the cart!`);
  };

  const removeFromCart = (productId) => {
    setCartItems(prevItems => prevItems.filter(item => item.id !== productId));
    toast.info("Item removed from cart.");
  };

  const updateQuantity = (productId, newQuantity) => {
    const itemToUpdate = cartItems.find(item => item.id === productId);
    if (!itemToUpdate) return;

    if (newQuantity > itemToUpdate.stock) {
      toast.warn(`Sorry, you cannot have ${newQuantity} of "${itemToUpdate.name}". We only have ${itemToUpdate.stock} in stock.`);
      return;
    }

    if (newQuantity < 1) {
      removeFromCart(productId);
    } else {
      setCartItems(prevItems =>
        prevItems.map(item =>
          item.id === productId ? { ...item, quantity: newQuantity } : item
        )
      );
    }
  };

  const clearCart = () => {
    setCartItems([]);
    toast.info("Cart has been cleared.");
  };

  const value = useMemo(
    () => ({
      cartItems,
      addToCart,
      removeFromCart,
      updateQuantity,
      clearCart,
    }),
    [cartItems]
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