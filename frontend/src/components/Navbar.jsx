import { Link } from 'react-router-dom'; // 1. Importamos el componente Link
import styles from './Navbar.module.css';

function Navbar() {
  return (
    <header className={styles.navbar}>
      <h1>My Online Store</h1>
      <nav className={styles.navLinks}>
        {/* 2. Reemplazamos <a> con <Link> y href con 'to' */}
        <Link to="/">Home</Link>
        <Link to="/cart">View Cart</Link>
        <Link to="/login">Login</Link>
      </nav>
    </header>
  );
}

export default Navbar;