// =================================================================
// FILE: ProductCard.jsx (FULL AND TRANSLATED VERSION)
// =================================================================

import styles from './ProductCard.module.css';

// This component receives a 'product' object as a prop.
// We use object destructuring { product } to directly access it.
function ProductCard({ product }) {
  // Defensive check: If for some reason no product is passed, render nothing.
  if (!product) {
    return null;
  }

  return (
    <div className={styles.card}>
      {/* 
        We use a placeholder image if the product doesn't have one.
        This makes our UI more robust.
      */}
      <img 
        src={product.imageUrl || 'https://via.placeholder.com/300'} 
        alt={product.name} 
        className={styles.image} 
      />
      
      <h3 className={styles.name}>{product.name}</h3>
      
      {/* 
        The .toFixed(2) method ensures the price is always displayed 
        with two decimal places (e.g., 79.99 instead of 79.9).
      */}
      <p className={styles.price}>${product.price ? product.price.toFixed(2) : '0.00'}</p>
      
      <p className={styles.stock}>Remaining: {product.stock}</p>
      
      <button className={styles.button}>Add to Cart</button>
    </div>
  );
}

export default ProductCard;