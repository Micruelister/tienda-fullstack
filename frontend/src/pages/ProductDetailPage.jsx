// =================================================================
// FILE: ProductDetailPage.jsx (SCROLLABLE DESCRIPTION VERSION)
// =================================================================

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext.jsx';
import axiosInstance from '../api/axiosInstance.js';
import { toast } from 'react-toastify';
import styles from './ProductDetailPage.module.css'; // Uses its own dedicated stylesheet
import '../App.css'; // For the global .container class

function ProductDetailPage() {
  // useParams gets the dynamic ':id' part from the URL
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Get the addToCart function from our global CartContext
  const { addToCart } = useCart();
  
  // State to hold the specific product's data
  const [product, setProduct] = useState(null);
  // State to handle the loading UI
  const [loading, setLoading] = useState(true);

  // This effect runs when the component mounts or when the 'id' in the URL changes
  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get(`/api/products/${id}`);
        setProduct(response.data);
      } catch (error) {
        console.error("Error fetching product details:", error);
        toast.error("Could not find the requested product.");
        navigate('/'); // Redirect user to homepage if product is not found
      } finally {
        setLoading(false);
      }
    };
    
    fetchProduct();
  }, [id, navigate]); // Dependencies for the effect

  // Handler function for the "Add to Cart" button click
  const handleAddToCart = () => {
    if (product) {
      addToCart(product);
    }
  };

  // Show a loading message while the product data is being fetched
  if (loading) {
    return <main className="container"><p>Loading product details...</p></main>;
  }

  // Show a message if the product could not be found after fetching
  if (!product) {
    return (
      <main className="container" style={{textAlign: 'center'}}>
        <h2>Product Not Found</h2>
        <p>The product you are looking for does not exist.</p>
        <Link to="/">Back to Homepage</Link>
      </main>
    );
  }

  // Once data is loaded, render the full page details
  return (
    <main className="container">
      <div className={styles.detailLayout}>
        <div className={styles.imageContainer}>
          <img src={product.imageUrl || 'https://via.placeholder.com/500'} alt={product.name} />
        </div>
        <div className={styles.infoContainer}>
          <h2 className={styles.productTitle}>{product.name}</h2>
          <p className={styles.price}>${product.price ? product.price.toFixed(2) : '0.00'}</p>
          <p className={styles.stock}>
            {product.stock > 0 ? `${product.stock} units remaining` : 'Out of Stock'}
          </p>
          <hr className={styles.divider} />
          
          {/* 
            The product description is now rendered inside a simple paragraph.
            The CSS class 'styles.description' will handle the scrolling box.
          */}
          <p className={styles.description}>
            {product.description || 'No description available for this product.'}
          </p>
          
          <button 
            onClick={handleAddToCart} 
            className={styles.addToCartButton}
            disabled={product.stock === 0}
          >
            {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
          </button>
        </div>
      </div>
    </main>
  );
}

export default ProductDetailPage;