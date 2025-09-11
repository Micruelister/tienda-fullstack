// Contenido actualizado para frontend/src/App.jsx

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
// Componentes y Páginas
import Navbar from './components/Navbar.jsx';
import ProtectedRoute from './components/auth/ProtectedRoute.jsx'; // 1. Importa a nuestro guardia
import HomePage from './pages/HomePage.jsx';
import CartPage from './pages/CartPage.jsx';
import ProductDetailPage from './pages/ProductDetailPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import MyAccountPage from './pages/MyAccountPage.jsx';
import ManageInventoryPage from './pages/ManageInventoryPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';

function App() {
  return (
    <BrowserRouter>
      <Navbar /> 
      <ToastContainer
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />      
      <Routes>
        {/* --- Rutas Públicas (Cualquiera puede verlas) --- */}
        <Route path="/" element={<HomePage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/product/:id" element={<ProductDetailPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* --- Rutas Protegidas para Usuarios Logueados --- */}
        {/* 2. Creamos una "ruta padre" que usa nuestro guardia */}
        <Route element={<ProtectedRoute />}>
          {/* Todas las rutas que estén DENTRO de esta serán protegidas */}
          <Route path="/my-account" element={<MyAccountPage />} />
          {/* En el futuro, la página de checkout también iría aquí */}
          {/* <Route path="/checkout" element={<CheckoutPage />} /> */}
        </Route>

        {/* --- Rutas Protegidas solo para Administradores --- */}
        {/* 3. Creamos otra ruta padre que usa al guardia en modo "solo admin" */}
        <Route element={<ProtectedRoute adminOnly={true} />}>
          <Route path="/admin/inventory" element={<ManageInventoryPage />} />
          {/* Todas las futuras rutas de admin irían aquí */}
        </Route>
        {/* --- Rutas para Autenticación --- */}
        <Route path= "/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;