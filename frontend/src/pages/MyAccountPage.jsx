// Contenido COMPLETO para frontend/src/pages/MyAccountPage.jsx

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import axiosInstance from '../api/axiosInstance.js';
import { toast } from 'react-toastify';
import styles from './MyAccountPage.module.css'; // Crearemos este archivo
import '../App.css';

function MyAccountPage() {
  const { user, updateUser } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({ username: '', email: '' });
  const [saving, setSaving] = useState(false);
  
  // useEffect para buscar el historial de pedidos cuando la página carga
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get('/api/my-orders');
        setOrders(response.data);
      } catch (error) {
        console.error("Error fetching orders:", error);
        toast.error("Could not load order history.");
      } finally {
        setLoading(false);
      }
    };
    
    // Solo buscamos los pedidos si el usuario está cargado
    if (user) {
      fetchOrders();
    }
  }, [user]); // Se ejecuta cuando el estado 'user' cambia

// Rellenamos el formulario con los datos del usuario del contexto
  useEffect(() => {
    if (user) {
      setProfileData({
        username: user.username,
        email: user.email
      });
    }
  }, [user]);

  const handleProfileChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await axiosInstance.put('/api/user/profile', profileData);
      
      // ¡MUY IMPORTANTE! Actualizamos el estado global de autenticación con los nuevos datos
      updateUser(response.data.user); 
      
      toast.success(response.data.message);
      setIsEditing(false); // Volvemos al modo vista
    } catch (error) {
      const errorMessage = error.response?.data?.message || "Failed to update profile.";
      toast.error(errorMessage);
    } finally {
      setSaving(false);
    }
  };
  
  if (!user) {
    return <main className="container"><p>Loading user data...</p></main>;
  }
  
return (
    <main className="container">
      <h2>My Account</h2>
      <div className={styles.accountInfo}>
        <div className={styles.infoHeader}>
          <h3>Account Information</h3>
          
          {/* --- LÓGICA CORREGIDA PARA LOS BOTONES --- */}
          {/* SI NO estamos editando, muestra el botón "Edit Profile" */}
          {!isEditing && (
            <button onClick={() => setIsEditing(true)} className={styles.editButton}>
              Edit Profile
            </button>
          )}
        </div>
        
        {isEditing ? (
          // SI estamos editando, muestra el formulario CON los botones de guardar/cancelar
          <form onSubmit={handleProfileSave} className={styles.editForm}>
            <div className={styles.formGroup}>
              <label htmlFor="username">Username</label>
              <input type="text" id="username" name="username" value={profileData.username} onChange={handleProfileChange} />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="email">Email</label>
              <input type="email" id="email" name="email" value={profileData.email} onChange={handleProfileChange} />
            </div>
            <div className={styles.buttonGroup}>
              <button type="button" onClick={() => setIsEditing(false)} className={styles.cancelButton}>Cancel</button>
              <button type="submit" disabled={saving} className={styles.saveButton}>
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </form>
        ) : (
          // SI NO estamos editando, muestra la información estática
          <div className={styles.viewInfo}>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
          </div>
        )}
      </div>

      <div className={styles.orderHistory}>
        <h3>My Order History</h3>
        {loading ? (
          <p>Loading orders...</p>
        ) : orders.length === 0 ? (
          <p>You have not placed any orders yet.</p>
        ) : (
          <div className={styles.ordersList}>
            {orders.map(order => (
              <div key={order.id} className={styles.orderCard}>
                <div className={styles.orderHeader}>
                  <h4>Order #{order.id}</h4>
                  <span>Date: {order.date}</span>
                </div>
                <div className={styles.orderDetails}>
                  <p><strong>Total:</strong> ${order.total.toFixed(2)}</p>
                  <p><strong>Shipped to:</strong> {order.shipping_address}</p>
                  <h5>Items:</h5>
                  <ul>
                    {order.products.map((product, index) => (
                      <li key={index}>
                        {product.name} (x{product.quantity})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

export default MyAccountPage;