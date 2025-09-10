// Contenido para frontend/src/pages/MyAccountPage.jsx

import { useAuth } from '../context/AuthContext.jsx';
import '../App.css';

function MyAccountPage() {
  // Leemos la información del usuario de nuestra pizarra mágica global
  const { user } = useAuth();

  // Si por alguna razón llegamos aquí sin un usuario, mostramos un mensaje de carga o error.
  if (!user) {
    return (
      <main className="container">
        <p>Loading user data...</p>
      </main>
    );
  }

  return (
    <main className="container">
      <h2>My Account</h2>
      <p><strong>Welcome, {user.username}!</strong></p>
      <p>This is your account page. More features will be added soon.</p>
      {/* En el futuro, aquí mostraremos el historial de pedidos */}
    </main>
  );
}

export default MyAccountPage;