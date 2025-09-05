# =================================================================
# SECCIÓN 1: IMPORTACIONES
# Aquí traemos todas las herramientas que necesitamos de nuestras librerías.
# =================================================================
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
import stripe
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid  # Para generar nombres de archivo únicos
from flask_cors import CORS

# =================================================================
# SECCIÓN 2: CONFIGURACIÓN INICIAL
# Creamos la aplicación y configuramos todas nuestras herramientas.
# =================================================================
app = Flask(__name__, template_folder='../templates', static_folder='../static')
load_dotenv()  # Carga las variables de entorno desde el archivo .env
CORS(app) # Habilita CORS para toda la aplicación
# ...

# --- Configuración de la Base de Datos ---
# La dirección para conectar con nuestro almacén PostgreSQL.
# ¡¡¡ ASEGÚRATE DE CAMBIAR 'tu_contraseña' POR TU CONTRASEÑA REAL !!!
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Configuración de la Sesión y Llave Secreta ---
# Necesaria para que Flask pueda encriptar los datos de la sesión (como el carrito).
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# --- Configuración de Stripe ---
# Reemplaza 'sk_test_...' con tu propia clave secreta de Stripe.
stripe.api_key = os.getenv('STRIPE_API_KEY')
YOUR_DOMAIN = 'http://127.0.0.1:5000'

# --- Configuración de la Carpeta de Subidas ---
# Le decimos a la app dónde debe guardar las imágenes de los productos.
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'static/uploads/products')

# --- Inicialización de Extensiones ---
# Creamos las instancias de nuestras herramientas, conectándolas a la app.
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# =================================================================
# SECCIÓN 3: MODELOS DE DATOS (LOS PLANOS DE NUESTRO ALMACÉN)
# =================================================================
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200), nullable=True)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    total = db.Column(db.Float, nullable=False)
    direccion_envio = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    productos = db.relationship('ProductoPedido', backref='pedido', lazy=True)

class ProductoPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    producto = db.relationship('Producto', backref='pedidos', lazy=True)

# =================================================================
# SECCIÓN 4: DECORADOR DE AUTENTICACIÓN
# Un "guardia de seguridad" para nuestras rutas.
# =================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =================================================================
# SECCIÓN 5: RUTAS DE LA APLICACIÓN
# Las diferentes URLs de nuestra tienda y la lógica que ejecuta cada una.
# =================================================================

# --- Rutas de la Tienda Principal ---

@app.route('/')
def hola_mundo():
    # Buscamos todos los productos en nuestra base de datos
    productos = Producto.query.all()
    # Le decimos a Flask que muestre la página 'inicio.html' y le pasamos la lista de productos
    return render_template('inicio.html', productos=productos)
# --- API Endpoints para Productos ---

# Endpoint para obtener TODOS los productos
@app.route('/api/productos', methods=['GET'])
def get_productos():
    # 1. Consultamos todos los productos de la base de datos.
    productos = Producto.query.all()
    
    # 2. Creamos una lista de diccionarios para convertir los objetos a un formato compatible con JSON.
    productos_list = []
    for producto in productos:
        producto_data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'stock': producto.stock,
            # Construimos la URL completa de la imagen
            'imagen_url': url_for('static', filename='uploads/products/' + producto.imagen, _external=True) if producto.imagen else None
        }
        productos_list.append(producto_data)
        
    # 3. Flask automáticamente convierte los diccionarios y listas a formato JSON.
    return jsonify(productos_list)

# Endpoint para obtener UN SOLO producto por su ID
@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    
    producto_data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'precio': producto.precio,
        'stock': producto.stock,
        'imagen_url': url_for('static', filename='uploads/products/' + producto.imagen, _external=True) if producto.imagen else None
    }
    
    return jsonify(producto_data)

# --- Rutas de Autenticación de Usuarios ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        nuevo_usuario = Usuario(username=username, email=email, password_hash=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('¡Tu cuenta ha sido creada! Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_identity = request.form['login_identity'] # Usamos el nuevo nombre del campo
        password = request.form['password']
    
        # SQLAlchemy nos permite hacer una consulta OR (o una cosa O la otra)
        from sqlalchemy import or_
        usuario = Usuario.query.filter(
            or_(Usuario.username == login_identity, Usuario.email == login_identity)
        ).first()
        if usuario and bcrypt.check_password_hash(usuario.password_hash, password):
            session['user_id'] = usuario.id
            session['is_admin'] = usuario.is_admin
            flash('¡Has iniciado sesión con éxito!', 'success')
            return redirect(url_for('hola_mundo'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('carrito', None)
    session.pop('is_admin', None)
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('hola_mundo'))

# --- Ruta para ver los detalles de un solo producto ---
@app.route('/producto/<int:producto_id>')
def detalle_producto(producto_id):
    # 1. Buscamos el producto en la base de datos usando el ID que nos llega en la URL.
    #    get_or_404 es genial: si no lo encuentra, automáticamente muestra un error 404.
    producto = Producto.query.get_or_404(producto_id)
    
    # 2. Mostramos la página 'detalle_producto.html' y le pasamos el producto que encontramos.
    return render_template('detalle_producto.html', producto=producto)

# --- Rutas del Carrito de Compras ---
@app.route('/carrito/añadir/<int:producto_id>', methods=['POST'])
def añadir_al_carrito(producto_id):
    carrito = session.get('carrito', {})
    id_str = str(producto_id)
    carrito[id_str] = carrito.get(id_str, 0) + 1
    session['carrito'] = carrito
    return redirect(url_for('hola_mundo'))

@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', {})
    if not carrito:
        return render_template('carrito.html', items_del_carrito=[], precio_total=0)
    items_del_carrito = []
    precio_total = 0
    for id_str, cantidad in carrito.items():
        producto = Producto.query.get(int(id_str))
        if producto:
            subtotal = producto.precio * cantidad
            precio_total += subtotal
            items_del_carrito.append({'producto': producto, 'cantidad': cantidad, 'subtotal': subtotal})
    return render_template('carrito.html', items_del_carrito=items_del_carrito, precio_total=precio_total)

@app.route('/carrito/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    carrito = session.get('carrito', {})
    id_str = str(producto_id)
    if id_str in carrito:
        del carrito[id_str]
    session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))

@app.route('/carrito/vaciar', methods=['POST'])
def vaciar_carrito():
    session.pop('carrito', None)
    return redirect(url_for('ver_carrito'))

# --- Rutas del Proceso de Pago ---
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    carrito = session.get('carrito', {})
    if not carrito:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('hola_mundo'))
    
    items_del_carrito = []
    precio_total = 0
    for id_str, cantidad in carrito.items():
        producto = Producto.query.get(int(id_str))
        if producto:
            subtotal = producto.precio * cantidad
            precio_total += subtotal
            items_del_carrito.append({'producto': producto, 'cantidad': cantidad, 'subtotal': subtotal})

    if request.method == 'POST':
        try:
            line_items = []
            for item in items_del_carrito:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item['producto'].nombre},
                        'unit_amount': int(item['producto'].precio * 100),
                    },
                    'quantity': item['cantidad'],
                })
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=YOUR_DOMAIN + '/pedido/exito',
                cancel_url=YOUR_DOMAIN + '/pedido/cancelado',
            )
            session['direccion_envio'] = request.form['direccion']
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return str(e)

    return render_template('checkout.html', items_del_carrito=items_del_carrito, precio_total=precio_total)

@app.route('/pedido/exito')
def pedido_exito():
    carrito = session.get('carrito', {})
    direccion = session.get('direccion_envio', '')
    if not carrito or not direccion:
        flash('Hubo un problema procesando tu pedido.', 'danger')
        return redirect(url_for('hola_mundo'))
    
    items_del_carrito = []
    precio_total = 0
    for id_str, cantidad in carrito.items():
        producto = Producto.query.get(int(id_str))
        if producto:
            subtotal = producto.precio * cantidad
            precio_total += subtotal
            items_del_carrito.append({'producto': producto, 'cantidad': cantidad})

    nuevo_pedido = Pedido(total=precio_total, direccion_envio=direccion, user_id=session['user_id'])
    db.session.add(nuevo_pedido)
    for item in items_del_carrito:
        producto_pedido = ProductoPedido(cantidad=item['cantidad'], precio_unitario=item['producto'].precio, pedido=nuevo_pedido, producto=item['producto'])
        db.session.add(producto_pedido)
    db.session.commit()
    
    session.pop('carrito', None)
    session.pop('direccion_envio', None)
    
    flash('¡Gracias por tu compra! Tu pedido ha sido procesado.', 'success')
    return redirect(url_for('hola_mundo'))

@app.route('/pedido/cancelado')
def pedido_cancelado():
    flash('El pago fue cancelado. Puedes volver a intentarlo.', 'warning')
    return redirect(url_for('ver_carrito'))

# --- Rutas del Panel de Administración ---
@app.route('/admin/nuevo', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre_producto = request.form['nombre']
        precio_producto = request.form['precio']
        stock_producto = request.form['stock']
        imagen_guardada = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file.filename != '':
                extension = os.path.splitext(file.filename)[1]
                unique_filename = str(uuid.uuid4()) + extension
                filename = secure_filename(unique_filename)
                upload_path = app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                save_path = os.path.join(upload_path, filename)
                file.save(save_path)
                imagen_guardada = filename
        nuevo_producto = Producto(nombre=nombre_producto, precio=float(precio_producto), stock=int(stock_producto), imagen=imagen_guardada)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('¡Producto creado con éxito!', 'success')
        return redirect(url_for('gestionar_inventario'))
    return render_template('crear_producto.html')

@app.route('/admin/inventario')
@login_required
def gestionar_inventario():
    productos = Producto.query.all()
    return render_template('gestionar_inventario.html', productos=productos)

@app.route('/admin/editar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def editar_producto(producto_id):
    producto_a_editar = Producto.query.get_or_404(producto_id)
    
    if request.method == 'POST':
        # 1. Actualizamos los datos de texto
        producto_a_editar.nombre = request.form['nombre'] 
        producto_a_editar.precio = float(request.form['precio'])
        producto_a_editar.stock = int(request.form['stock'])
        
        # 2. Lógica para manejar la actualización de la imagen
        if 'imagen' in request.files:
            file = request.files['imagen']
            # Comprobamos si el usuario seleccionó un archivo nuevo
            if file.filename != '':
                # Guardamos el nombre de la imagen antigua para poder borrarla después
                imagen_antigua = producto_a_editar.imagen
                
                # Procesamos y guardamos la nueva imagen con un nombre único
                extension = os.path.splitext(file.filename)[1]
                unique_filename = str(uuid.uuid4()) + extension
                filename = secure_filename(unique_filename)
                
                upload_path = app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                save_path = os.path.join(upload_path, filename)
                file.save(save_path)
                
                # Actualizamos el producto con el nuevo nombre de archivo
                producto_a_editar.imagen = filename
                
                # ¡Paso CRUCIAL! Si había una imagen antigua, la eliminamos del servidor
                if imagen_antigua:
                    try:
                        os.remove(os.path.join(upload_path, imagen_antigua))
                    except OSError as e:
                        flash(f'Error al eliminar la imagen antigua: {e}', 'danger')

        # 3. Guardamos todos los cambios en la base de datos
        db.session.commit()
        flash('¡Producto actualizado con éxito!', 'success')
        return redirect(url_for('gestionar_inventario'))
        
    # Si es GET, la función no cambia: simplemente muestra el formulario
    return render_template('editar_producto.html', producto=producto_a_editar)

@app.route('/admin/eliminar/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_producto(producto_id):
    producto_a_eliminar = Producto.query.get_or_404(producto_id)
    if producto_a_eliminar.imagen:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], producto_a_eliminar.imagen))
        except OSError as e:
            flash(f'Error al eliminar el archivo de imagen: {e}', 'danger')
    db.session.delete(producto_a_eliminar)
    db.session.commit()
    flash('¡Producto eliminado con éxito!', 'success')
    return redirect(url_for('gestionar_inventario'))
# --- Rutas de la Cuenta de Usuario ---
# --- Rutas de la Cuenta de Usuario ---
@app.route('/mi-cuenta') # <-- CAMBIO 1: La URL ahora es más general.
@login_required
def mi_cuenta(): # <-- CAMBIO 2: El nombre de la función ahora es más general.
    user_id = session['user_id']
    pedidos_del_usuario = Pedido.query.filter_by(user_id=user_id).order_by(Pedido.fecha.desc()).all()
    
    # También vamos a obtener la información del usuario para mostrarla en la página.
    usuario = Usuario.query.get(user_id)
    
    return render_template('mi_cuenta.html', pedidos=pedidos_del_usuario, usuario=usuario)
# =================================================================
# SECCIÓN 6: ARRANQUE DEL SERVIDOR
# =================================================================
if __name__ == '__main__':
    app.run(debug=True)