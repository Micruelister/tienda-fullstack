// =================================================================
// FILE: CartPage.jsx (FULL AND INTERACTIVE VERSION)
// =================================================================

import { useCart } from '../context/CartContext.jsx';
import styles from './CartPage.module.css';
import '../App.css'; 

function CartPage() {
  // 1. Get the items AND the new management functions from our context
  const { cartItems, removeFromCart, updateQuantity, clearCart } = useCart();

  const totalPrice = cartItems.reduce((total, item) => total + item.price * item.quantity, 0);

  return (
    <main className="container">
      <h2>My Shopping Cart</h2>

      {cartItems.length === 0 ? (
        <p>Your shopping cart is empty. <a href="/">Go find something nice!</a></p>
      ) : (
        <> {/* Use a Fragment to group multiple elements */}
          <div className={styles.cartActionsHeader}>
            {/* 2. Add a button to clear the whole cart */}
            <button onClick={clearCart} className={styles.clearCartButton}>Clear Entire Cart</button>
          </div>
          <div className={styles.cartLayout}>
            <div className={styles.cartItems}>
              {cartItems.map(item => (
                <div key={item.id} className={styles.cartItem}>
                  <img src={item.imageUrl || 'https://via.placeholder.com/150'} alt={item.name} className={styles.itemImage} />
                  <div className={styles.itemDetails}>
                    <h3>{item.name}</h3>
                    {/* 3. Add controls to update quantity */}
                    <div className={styles.quantityControl}>
                      <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
                      <span>{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                    </div>
                    <p>Price: ${item.price.toFixed(2)}</p>
                  </div>
                  <div className={styles.itemActions}>
                    <p className={styles.itemSubtotal}>Subtotal: ${(item.price * item.quantity).toFixed(2)}</p>
                    {/* 4. Make the Remove button functional */}
                    <button onClick={() => removeFromCart(item.id)} className={styles.removeButton}>Remove</button>
                  </div>
                </div>
              ))}
            </div>
            <div className={styles.cartSummary}>
              {/* ... (Order Summary section remains the same) ... */}
              <h3>Order Summary</h3>
              <div className={styles.summaryLine}>
                <span>Subtotal</span>
                <span>${totalPrice.toFixed(2)}</span>
              </div>
              <div className={styles.summaryLine}>
                <span>Shipping</span>
                <span>FREE</span>
              </div>
              <hr />
              <div className={`${styles.summaryLine} ${styles.total}`}>
                <span>Total</span>
                <span>${totalPrice.toFixed(2)}</span>
              </div>
              <button className={styles.checkoutButton}>Proceed to Checkout</button>
            </div>
          </div>
        </>
      )}
    </main>
  );
}

export default CartPage;