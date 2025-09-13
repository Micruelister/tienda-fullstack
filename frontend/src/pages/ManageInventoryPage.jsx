// =================================================================
// FILE: ManageInventoryPage.jsx (FINAL VERSION WITH EDIT LINK)
// =================================================================

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import axiosInstance from '../api/axiosInstance';
import styles from './ManageInventoryPage.module.css';
import '../App.css';

function ManageInventoryPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Effect to fetch all products when the component first loads
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get('/api/products');
        if (!response.data) {
          throw new Error('Failed to fetch products');
        }
        setProducts(response.data);
      } catch (error) {
        toast.error(error.message || "Could not load product data.");
        console.error("Error fetching products:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, []); // The empty array [] ensures this runs only once on mount

  // Function to handle the deletion of a product
  const handleDelete = async (productId) => {
    if (!window.confirm("Are you sure you want to delete this product permanently? This action cannot be undone.")) {
      return;
    }

    try {
      const response = await axiosInstance.delete(`/api/products/${productId}`);
      
      // Update the UI instantly by removing the product from the local state
      setProducts(currentProducts => currentProducts.filter(p => p.id !== productId));

      toast.success(response.data.message);

    } catch (error) {
      const errorMessage = error.response?.data?.message || "Failed to delete product.";
      toast.error(errorMessage);
      console.error("Error deleting product:", error);
    }
  };

  if (loading) {
    return <main className="container"><p>Loading inventory...</p></main>;
  }

  return (
    <main className="container">
      <div className={styles.header}>
        <h2>Manage Product Inventory</h2>
        <div>
          <Link to="/admin/product/new" className={styles.addButton}>Add New Product</Link>
        </div>
      </div>

      <div className={styles.tableContainer}> {/* Added a wrapper for potential horizontal scroll on small screens */}
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
                  {/* --- THIS IS THE KEY CHANGE --- */}
                  {/* The "Edit" button is now a Link that navigates to the edit page */}
                  <Link 
                    to={`/admin/product/edit/${product.id}`} 
                    className={styles.actionButton}
                  >
                    Edit
                  </Link>

                  <button 
                    onClick={() => handleDelete(product.id)}
                    className={`${styles.actionButton} ${styles.deleteButton}`}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}

export default ManageInventoryPage;