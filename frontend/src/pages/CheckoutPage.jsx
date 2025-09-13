// =================================================================
// FILE: CheckoutPage.jsx (FULL VERSION WITH STRUCTURED ADDRESS FORM)
// =================================================================

import { useState } from 'react';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import axiosInstance from '../api/axiosInstance.js';
import { toast } from 'react-toastify';
import styles from './CheckoutPage.module.css';
import '../App.css';
import { schengenCountries } from '../utils/countries.js'; // We import our new country list

function CheckoutPage() {
  const { cartItems } = useCart();
  const { user } = useAuth();
  
  // Create a single state object to hold all address fields
  const [address, setAddress] = useState({
    fullName: user?.username || '', // Pre-fill with username if available
    streetAddress: '',
    city: '',
    postalCode: '',
    country: 'Spain', // Set a default country from the list
  });

  const [loading, setLoading] = useState(false);

  // A single handler function to update any address field
  const handleAddressChange = (e) => {
    // e.target.name will be "fullName", "city", etc.
    // e.target.value is what the user typed
    setAddress({ ...address, [e.target.name]: e.target.value });
  };

  const handleCheckout = async () => {
    // Simple validation to ensure fields are not empty
    if (!address.fullName || !address.streetAddress || !address.city || !address.postalCode || !address.country) {
      toast.error("Please fill in all address fields.");
      return;
    }

    setLoading(true);
    try {
      const response = await axiosInstance.post('/api/create-checkout-session', {
        cartItems: cartItems,
        shippingAddress: address // Send the entire address object
      });
      const { url } = response.data;
      window.location.href = url;
    } catch (error) {
      const errorMessage = error.response?.data?.message || "Checkout failed. Please try again.";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
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
          <h3>Shipping Information</h3>
          {/* --- NEW STRUCTURED ADDRESS FORM --- */}
          <div className={styles.addressForm}>
            <div className={styles.formGroup}>
              <label htmlFor="fullName">Full Name</label>
              <input type="text" id="fullName" name="fullName" value={address.fullName} onChange={handleAddressChange} required />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="country">Country</label>
              <select id="country" name="country" value={address.country} onChange={handleAddressChange} required>
                {/* We dynamically create an <option> for each country in our list */}
                {schengenCountries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="streetAddress">Street Address</label>
              <input type="text" id="streetAddress" name="streetAddress" value={address.streetAddress} onChange={handleAddressChange} required placeholder="e.g., 123 Main St" />
            </div>
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="city">City</label>
                <input type="text" id="city" name="city" value={address.city} onChange={handleAddressChange} required />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="postalCode">Postal Code</label>
                <input type="text" id="postalCode" name="postalCode" value={address.postalCode} onChange={handleAddressChange} required />
              </div>
            </div>
          </div>
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
              <span>${cartItems.reduce((total, item) => total + item.price * item.quantity, 0).toFixed(2)}</span>
            </div>
            <button onClick={handleCheckout} disabled={loading} className={styles.payButton}>
              {loading ? 'Processing...' : 'Proceed to Payment'}
            </button>
        </div>
      </div>
    </main>
  );
}

export default CheckoutPage;