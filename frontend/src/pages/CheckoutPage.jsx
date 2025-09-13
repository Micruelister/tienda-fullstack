// Contenido para frontend/src/pages/CheckoutPage.jsx

import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import axiosInstance from '../api/axiosInstance.js';
import { toast } from 'react-toastify';
import styles from './CheckoutPage.module.css'; // Crearemos este archivo
import '../App.css';

function CheckoutPage() {
  const { cartItems } = useCart();
  const { user } = useAuth();

  const totalPrice = cartItems.reduce((total, item) => total + item.price * item.quantity, 0);

  const handleCheckout = async () => {
    try {
      // 1. Enviamos los items del carrito a nuestro backend
      const response = await axiosInstance.post('/api/create-checkout-session', {
        cartItems: cartItems
      });

      // 2. El backend nos devuelve la URL de Stripe
      const { url } = response.data;

      // 3. Redirigimos al usuario a la página de pago de Stripe
      window.location.href = url;

    } catch (error) {
      const errorMessage = error.response?.data?.message || "Checkout failed. Please try again.";
      toast.error(errorMessage);
    }
  };

  if (cartItems.length === 0) {
    return (
      <main className="container">
        <h2>Checkout</h2>
        <p>Your cart is empty. There is nothing to check out.</p>
      </main>
    );
  }

  return (
    <main className="container">
      <h2>Confirm Your Order</h2>
      <div className={styles.checkoutLayout}>
        <div className={styles.orderDetails}>
          <h3>Shipping to:</h3>
          <p>{user?.username || 'Guest'}</p>
          <p>{user?.email || 'Please log in'}</p>
          {/* Aquí podríamos añadir un formulario para la dirección de envío */}
          <hr />
          <h3>Order Items:</h3>
          {cartItems.map(item => (
            <div key={item.id} className={styles.item}>
              <span>{item.name} (x{item.quantity})</span>
              <span>${(item.price * item.quantity).toFixed(2)}</span>
            </div>
          ))}
        </div>
        <div className={styles.orderSummary}>
            <h3>Order Summary</h3>
             <div className={styles.summaryLine}>
              <span>Total</span>
              <span>${totalPrice.toFixed(2)}</span>
            </div>
            <button onClick={handleCheckout} className={styles.payButton}>
              Proceed to Payment
            </button>
        </div>
      </div>
    </main>
  );
}

export default CheckoutPage;