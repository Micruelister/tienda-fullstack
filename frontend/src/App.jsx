// =================================================================
// FILE: App.jsx (FULL AND CURRENT VERSION)
// PURPOSE: Sets up the main application routing.
// =================================================================

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import HomePage from './pages/HomePage.jsx';
import CartPage from './pages/CartPage.jsx';
import ProductDetailPage from './pages/ProductDetailPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import MyAccountPage from './pages/MyAccountPage.jsx';
import ManageInventoryPage from './pages/ManageInventoryPage.jsx';

// The App component is the root of our application's component tree.
// Its main job is to define the structure of the pages and the navigation.
function App() {
  return (
    // <BrowserRouter> is the component that enables client-side routing.
    // It should wrap your entire application.
    <BrowserRouter>

      {/* 
        The <Navbar> is placed outside of the <Routes> component.
        This means it will be rendered on EVERY "page" of our application,
        providing consistent navigation.
      */}
      <Navbar /> 

      {/*
        The <Routes> component is a container for all of our individual routes.
        It looks at the current URL and renders the first matching <Route>.
      */}
      <Routes>
        {/* Each <Route> defines a mapping between a URL path and a component. */}
        
        {/* When the URL is exactly "/", render the HomePage component. */}
        <Route path="/" element={<HomePage />} />
        
        {/* When the URL is "/cart", render the CartPage component. */}
        <Route path="/cart" element={<CartPage />} />
        
        {/* 
          This is a dynamic route. The ":id" part is a URL parameter.
          It will match URLs like "/product/1", "/product/2", etc.
          React Router will make the 'id' value available to the ProductDetailPage component.
        */}
        <Route path="/product/:id" element={<ProductDetailPage />} />

        {/* When the URL is "/login", render the LoginPage component. */}
        <Route path="/login" element={<LoginPage />} />

        {/* In the future, we will add more routes here, for example: */}
        {/* <Route path="/register" element={<RegisterPage />} /> */}
        {/* <Route path="/my-account" element={<AccountPage />} /> */}

        <Route path="/my-account" element={<MyAccountPage />} />
        <Route path="/admin/inventory" element={<ManageInventoryPage />} />
        {/* Add more routes as needed */}

      </Routes>

    </BrowserRouter>
  );
}

export default App;