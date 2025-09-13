// =================================================================
// FILE: EditProductPage.jsx (FULL AND COMPLETE VERSION)
// PURPOSE: Allows admins to edit an existing product.
// =================================================================

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import axiosInstance from '../api/axiosInstance';
import styles from './AuthForm.module.css'; // Reusing our consistent form styles

function EditProductPage() {
  // useParams gets the dynamic part of the URL (the product's ID)
  const { id } = useParams();
  const navigate = useNavigate();

  // State for each form field
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');
  const [currentImage, setCurrentImage] = useState(''); // URL of the existing image
  const [newImage, setNewImage] = useState(null);      // The new image file to upload
  
  // State for UI feedback
  const [loading, setLoading] = useState(true);   // For the initial data fetch
  const [saving, setSaving] = useState(false);     // For the form submission process

  // This useEffect runs once when the component mounts to fetch the existing product data
  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get(`/api/products/${id}`);
        const product = response.data;
        
        // Populate the form fields with the data received from the API
        setName(product.name);
        setPrice(product.price);
        setStock(product.stock);
        setCurrentImage(product.imageUrl);
      } catch (error) {
        toast.error("Failed to load product data.");
        navigate('/admin/inventory'); // Redirect if the product can't be found
      } finally {
        setLoading(false);
      }
    };
    
    fetchProduct();
  }, [id, navigate]); // It re-runs if the 'id' in the URL changes

  // This function handles the form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);

    const formData = new FormData();
    formData.append('name', name);
    formData.append('price', price);
    formData.append('stock', stock);
    if (newImage) {
      formData.append('image', newImage);
    }

    try {
      const response = await axiosInstance.post(`/api/products/${id}`, formData);
      toast.success(response.data.message);
      navigate('/admin/inventory'); // Redirect back to the inventory list on success
    } catch (error) {
      const errorMessage = error.response?.data?.message || "Failed to update product.";
      toast.error(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  // Show a loading message while fetching initial product data
  if (loading) {
    return <main className="container"><p>Loading product data...</p></main>;
  }

  return (
    <div className={styles.formContainer}>
      <h2>Edit Product</h2>
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label htmlFor="name">Product Name:</label>
          <input
            className={styles.formInput}
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="price">Price:</label>
          <input
            className={styles.formInput}
            type="number"
            id="price"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            step="0.01"
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="stock">Stock:</label>
          <input
            className={styles.formInput}
            type="number"
            id="stock"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label>Current Image:</label>
          {currentImage ? 
            <img src={currentImage} alt="Current product" style={{width: '100px', height: '100px', objectFit: 'cover', borderRadius: '4px'}} /> :
            <p style={{fontSize: '0.9rem', color: '#777'}}>No image on file.</p>
          }
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="image">Upload New Image (optional):</label>
          <input
            className={styles.formInput}
            type="file"
            id="image"
            accept="image/*"
            onChange={(e) => setNewImage(e.target.files[0])}
          />
        </div>
        <button type="submit" className={styles.submitButton} disabled={saving}>
          {saving ? 'Saving Changes...' : 'Save Changes'}
        </button>
      </form>
       <p className={styles.switchFormLink}>
        <Link to="/admin/inventory">Back to Inventory</Link>
      </p>
    </div>
  );
}

export default EditProductPage;