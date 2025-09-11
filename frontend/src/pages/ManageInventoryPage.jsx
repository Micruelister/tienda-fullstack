// =================================================================
// FILE: ManageInventoryPage.jsx (FUNCTIONAL VERSION)
// =================================================================

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom'; // To link to "Add Product" page
import styles from './ManageInventoryPage.module.css'; // We'll create this file
import '../App.css';

function ManageInventoryPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch all products when the component mounts
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:5000/api/products');
        if (!response.ok) throw new Error('Failed to fetch products');
        const data = await response.json();
        setProducts(data);
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  if (loading) {
    return <main className="container"><p>Loading inventory...</p></main>;
  }

  return (
    <main className="container">
      <div className={styles.header}>
        <h2>Manage Product Inventory</h2>
        {/* We will create the "/admin/product/new" route later */}
        <Link to="/admin/product/new" className={styles.addButton}>Add New Product</Link>
      </div>

      <table className={styles.inventoryTable}>
        <thead>
          <tr>
            <th>Image</th>
            <th>Name</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id}>
              <td>
                <img src={product.imageUrl || 'https://via.placeholder.com/150'} alt={product.name} />
              </td>
              <td>{product.name}</td>
              <td>${product.price.toFixed(2)}</td>
              <td>{product.stock}</td>
              <td>
                <button className={styles.actionButton}>Edit</button>
                <button className={`${styles.actionButton} ${styles.deleteButton}`}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

export default ManageInventoryPage;