// =================================================================
// FILE: CartContext.jsx (FULL VERSION WITH MANAGEMENT FUNCTIONS)
// =================================================================

import { createContext, useState, useContext, useMemo, use } from 'react';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [cartItems, setCartItems] = useState([]);

  // --- ADD ITEM ---
  const addToCart = (product) => {
    const existingItem = cartItems.find(item => item.id === product.id);
    if (existingItem) {
      setCartItems(cartItems.map(item => 
        item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
      ));
    } else {
      setCartItems([...cartItems, { ...product, quantity: 1 }]);
    }
  };

  // --- REMOVE ITEM ---
  // Filters the cartItems array, keeping every item EXCEPT the one with the matching id.
  const removeFromCart = (productId) => {
    setCartItems(cartItems.filter(item => item.id !== productId));
  };

  // --- UPDATE QUANTITY ---
  // Maps over the items. If an item's id matches, it returns a new item object with the updated quantity.
  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity < 1) {
      // If the new quantity is 0 or less, just remove the item
      removeFromCart(productId);
    } else {
      setCartItems(cartItems.map(item =>
        item.id === productId ? { ...item, quantity: newQuantity } : item
      ));
    }
  };

  // --- CLEAR CART ---
  // Simply sets the cart back to an empty array.
  const clearCart = () => {
    setCartItems([]);
  };

  // We make all functions and the state available to the rest of the app.
  const value = useMemo(() => ({ cartItems, addToCart, removeFromCart, updateQuantity, clearCart }), [cartItems]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  return useContext(CartContext);
}