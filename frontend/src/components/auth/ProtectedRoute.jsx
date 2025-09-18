// Contenido para frontend/src/components/auth/ProtectedRoute.jsx

import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

function ProtectedRoute({ adminOnly = false }) {
  const { user, loading } = useAuth();

  // Mientras se verifica la sesión, no renderizamos nada para evitar parpadeos.
  if (loading) {
    return null; // O un componente de Spinner/Cargando...
  }

  // Después de cargar, verificamos los permisos.

  // CASO 1: Ruta de admin, pero el usuario no es admin o no está logueado.
  if (adminOnly && (!user || !user.is_admin)) {
    return <Navigate to="/" replace />;
  }

  // CASO 2: Ruta protegida normal, pero el usuario no está logueado.
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // CASO 3: El usuario tiene los permisos necesarios.
  return <Outlet />;
}

export default ProtectedRoute;