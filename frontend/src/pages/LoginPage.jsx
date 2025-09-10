// =================================================================
// FILE: LoginPage.jsx (FULL AND FUNCTIONAL VERSION)
// PURPOSE: Handles user login form and authentication logic.
// =================================================================

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import '../App.css'; // Reusing the .container styles

function LoginPage() {
  // State for the form inputs. These are "controlled components".
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null); // State to hold any login error messages
  const [loading, setLoading] = useState(false); // State to handle loading state of the button

  // Get the login function from our global AuthContext
  const { login } = useAuth();
  
  // Get the navigate function from React Router to redirect the user after login
  const navigate = useNavigate();

  // This function is called when the form is submitted
  const handleSubmit = async (event) => {
    // Prevent the default form behavior (page reload)
    event.preventDefault();
    
    // Set loading state to true to disable the button and show feedback
    setLoading(true);
    setError(null); // Clear previous errors

    try {
      // Send a POST request to our Flask API's login endpoint
      const response = await fetch('http://127.0.0.1:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // Tell the server we're sending JSON
        },
        // Convert the email and password state into a JSON string
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      // If the response is not "ok" (e.g., 401 Unauthorized), throw an error
      if (!response.ok) {
        throw new Error(data.message || 'Failed to login');
      }
      
      // If the login is successful:
      console.log('Login successful:', data);
      
      // 1. Call the global 'login' function from AuthContext with the user data
      login(data.user);
      
      // 2. Redirect the user to the homepage
      navigate('/');

    } catch (err) {
      // If any error occurs, update the error state to display it to the user
      console.error('Login error:', err);
      setError(err.message);
    } finally {
      // This will run whether the login succeeds or fails
      setLoading(false); // Set loading back to false
    }
  };

  return (
    <main className="container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email">Email Address or Username:</label>
          <input 
            type="text" 
            id="email" 
            name="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required 
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input 
            type="password" 
            id="password" 
            name="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required 
          />
        </div>
        {/* Display the error message if it exists */}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        {/* Disable the button while loading to prevent multiple submissions */}
        <button type-="submit" disabled={loading}>
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>
    </main>
  );
}

export default LoginPage;