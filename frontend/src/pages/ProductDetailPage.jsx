import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; // 1. Importamos el Hook para leer parámetros
import '../App.css'; // Reutilizamos estilos

function ProductDetailPage() {
  // 2. Usamos el Hook useParams para obtener los parámetros de la URL
  const { id } = useParams(); // 'id' debe coincidir con el nombre del parámetro en la ruta

  const [product, setProduct] = useState(null); // Estado para guardar el producto. Inicialmente null.
  const [loading, setLoading] = useState(true); // Estado para saber si estamos cargando

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        // 3. Usamos el productId de la URL para llamar a la API correcta
        const response = await fetch(`http://127.0.0.1:5000/api/products/${id}`);
        if (!response.ok) throw new Error('Product not found');
        const data = await response.json();
        setProduct(data);
      } catch (error) {
        console.error("Error fetching product:", error);
      } finally {
        setLoading(false); // Dejamos de cargar, tanto si hubo éxito como si hubo error
      }
    };
    if (id){
      fetchProduct();
    }

  }, [id]); // 4. El efecto se volverá a ejecutar si el productId cambia

  // 5. Mostramos diferentes cosas dependiendo del estado
  if (loading) {
    return <p className="container">Loading product details...</p>;
  }

  if (!product) {
    return <p className="container">Product not found.</p>;
  }

  return (
    <main className="container">
      {/* ¡Aquí irá el diseño de nuestra página de detalles! */}
      <h2>{product.name}</h2>
      <img src={product.imageUrl || 'https://via.placeholder.com/400'} alt={product.name} style={{maxWidth: '400px'}} />
      <h3>${product.price ? product.price.toFixed(2) : '0.00'}</h3>
      <p>Stock: {product.stock}</p>
      <button>Add to Cart</button>
    </main>
  );
}

export default ProductDetailPage;