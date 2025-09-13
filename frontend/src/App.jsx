// =================================================================
// FILE: App.jsx (FULL, CORRECTED, AND COMPLETE VERSION)
// =================================================================

import { BrowserRouter, Routes, Route } from 'react-router-dom';

// --- Toastify Imports ---
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// --- Layout & Auth Components ---
import Navbar from './components/Navbar.jsx';
import ProtectedRoute from './components/auth/ProtectedRoute.jsx';

// --- Page Components (ALL OF THEM) ---
import HomePage from './pages/HomePage.jsx';
import CartPage from './pages/CartPage.jsx';
import ProductDetailPage from './pages/ProductDetailPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import MyAccountPage from './pages/MyAccountPage.jsx';
import ManageInventoryPage from './pages/ManageInventoryPage.jsx';
import CreateProductPage from './pages/CreateProductPage.jsx';
import EditProductPage from './pages/EditProductPage.jsx';
import CheckoutPage from './pages/CheckoutPage.jsx';
import OrderSuccessPage from './pages/OrderSuccessPage.jsx';
import OrderCancelPage from './pages/OrderCancelPage.jsx';

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
        
        {/* --- PUBLIC ROUTES --- */}
        <Route path="/" element={<HomePage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/product/:id" element={<ProductDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* --- PROTECTED ROUTES FOR LOGGED-IN USERS --- */}
        <Route element={<ProtectedRoute />}>
          <Route path="/my-account" element={<MyAccountPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/order/success" element={<OrderSuccessPage />} />
          <Route path="/order/cancel" element={<OrderCancelPage />} />  
        </Route>

        {/* --- PROTECTED ROUTES FOR ADMINS ONLY --- */}
        <Route element={<ProtectedRoute adminOnly={true} />}>
          <Route path="/admin/inventory" element={<ManageInventoryPage />} />
          <Route path="/admin/product/new" element={<CreateProductPage />} />
          <Route path="/admin/product/edit/:id" element={<EditProductPage />} /> {/* Añade la ruta */}
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;