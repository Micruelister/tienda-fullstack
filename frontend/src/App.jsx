import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import HomePage from './pages/HomePage.jsx';
import CartPage from './pages/CartPage.jsx';

function App() {
  return (
    // 1. El BrowserRouter es el que activa toda la magia del enrutamiento.
    <BrowserRouter>
      {/* La Navbar ahora está fuera de las Rutas, por lo que se mostrará en TODAS las páginas */}
      <Navbar /> 

      {/* El componente Routes es donde definimos nuestro mapa */}
      <Routes>
        {/* 2. Cada Route es una regla del mapa */}
        <Route path="/" element={<HomePage />} />
        <Route path="/cart" element={<CartPage />} />
        {/* Agregaremos más rutas aquí en el futuro (login, producto, etc.) */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;