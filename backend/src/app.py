# =================================================================
# FILE: app.py (ABSOLUTELY 100% COMPLETE DEBUGGING VERSION)
# =================================================================
import os
import uuid
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, jsonify, render_template, request, redirect,
                   url_for, session, flash)
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import stripe
app = Flask(__name__, template_folder='../templates', static_folder='../static')
load_dotenv()

# --- SIMPLIFIED & ROBUST CONFIGURATION FOR DEBUGGING ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Allow cross-site cookies
app.config['SESSION_COOKIE_SECURE'] = True # Ensure cookies are only sent over HTTPS
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True # Signs the cookie id
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True # Ensure cookies are only sent over HTTPS
Session(app)

# Use a simple, wide-open CORS configuration for debugging purposes
CORS(app, origins="http://localhost:5173", supports_credentials=True)

# --- Other Configurations ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'static/uploads/products')
stripe.api_key = os.getenv('STRIPE_API_KEY')
YOUR_DOMAIN = 'http://127.0.0.1:5000'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# =================================================================
# SECTION 3: DATA MODELS
# =================================================================
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(200), nullable=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    total = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    products = db.relationship('OrderProduct', backref='order', lazy=True)

class OrderProduct(db.Model):
    __tablename__ = 'order_products'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref='orders', lazy=True)

# =================================================================
# SECTION 4: DECORATORS
# =================================================================
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("--- SESSION CHECK ---")
        print(session)
        print("---------------------")
        if 'user_id' not in session:
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# =================================================================
# SECTION 5: API ROUTES
# =================================================================

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock': product.stock,
            'imageUrl': url_for('static', filename=f'uploads/products/{product.image_filename}', _external=True) if product.image_filename else None
        }
        products_list.append(product_data)
    return jsonify(products_list)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_data = {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'stock': product.stock,
        'imageUrl': url_for('static', filename=f'uploads/products/{product.image_filename}', _external=True) if product.image_filename else None
    }
    return jsonify(product_data)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Username, email, and password are required"}), 400
    username, email, password = data.get('username'), data.get('email'), data.get('password')
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exists"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400
    login_identity, password = data.get('email'), data.get('password')
    user = User.query.filter(or_(User.username == login_identity, User.email == login_identity)).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        session.modified = True
        return jsonify({"message": "Login successful!", "user": {"id": user.id, "username": user.username, "is_admin": user.is_admin}}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/admin/product/new', methods=['POST'])
@api_login_required
def create_product():
    if not session.get('is_admin'):
        return jsonify({"message": "Admin access required"}), 403
    if 'name' not in request.form or 'price' not in request.form or 'stock' not in request.form:
        return jsonify({"message": "Name, price, and stock are required fields."}), 400
    product_name, product_price, product_stock = request.form['name'], request.form['price'], request.form['stock']
    saved_image_filename = None
    if 'image' in request.files:
        file = request.files.get('image')
        if file and file.filename != '':
            extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{extension}"
            filename = secure_filename(unique_filename)
            upload_path = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_path, exist_ok=True)
            save_path = os.path.join(upload_path, filename)
            file.save(save_path)
            saved_image_filename = filename
    new_product = Product(name=product_name, price=float(product_price), stock=int(product_stock), image_filename=saved_image_filename)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product created successfully!", "productId": new_product.id}), 201

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@api_login_required
def delete_api_product(product_id):
    if not session.get('is_admin'):
        return jsonify({"message": "Admin access required"}), 403
    product_to_delete = Product.query.get_or_404(product_id)
    if product_to_delete.image_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product_to_delete.image_filename))
        except OSError as e:
            print(f"Error deleting image file: {e}")
    db.session.delete(product_to_delete)
    db.session.commit()
    return jsonify({"message": f"Product '{product_to_delete.name}' deleted successfully"}), 200
# En app.py

@app.route('/api/products/<int:product_id>', methods=['POST']) # Usaremos POST para simplicidad con FormData
@api_login_required
def update_product(product_id):
    if not session.get('is_admin'):
        return jsonify({"message": "Admin access required"}), 403

    product_to_update = Product.query.get_or_404(product_id)
    
    # Actualizamos los campos con los datos del formulario
    product_to_update.name = request.form.get('name', product_to_update.name)
    product_to_update.price = float(request.form.get('price', product_to_update.price))
    product_to_update.stock = int(request.form.get('stock', product_to_update.stock))

    # Lógica para actualizar la imagen si se envía una nueva
    if 'image' in request.files:
        file = request.files.get('image')
        if file and file.filename != '':
            # Borramos la imagen antigua si existe
            if product_to_update.image_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product_to_update.image_filename))
                except OSError as e:
                    print(f"Error deleting old image file: {e}")
            
            # Guardamos la nueva imagen
            extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{extension}"
            filename = secure_filename(unique_filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            product_to_update.image_filename = filename

    db.session.commit()
    return jsonify({"message": f"Product '{product_to_update.name}' updated successfully"}), 200

# En app.py

@app.route('/api/create-checkout-session', methods=['POST'])
@api_login_required
def create_checkout_session():
    data = request.get_json()
    cart_items = data.get('cartItems')

    if not cart_items:
        return jsonify({"message": "Cart is empty"}), 400
    YOUR_FRONTEND_DOMAIN = 'http://localhost:5173'

    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'EUR',
                'product_data': {
                    'name': item['name'],
                    'images': [item['imageUrl']],
                },
                'unit_amount': int(item['price'] * 100), # Stripe necesita el precio en centavos
            },
            'quantity': item['quantity'],
        })

    try:
        # Hablamos con Stripe para crear la sesión
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # Las URLs a las que Stripe redirigirá al usuario después del pago
            success_url=YOUR_FRONTEND_DOMAIN + '/order/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_FRONTEND_DOMAIN + '/order/cancel',
        )
        # Devolvemos la URL de la sesión de pago a nuestro frontend
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500
# En app.py

@app.route('/api/order/verify', methods=['POST'])
@api_login_required
def verify_order():
    data = request.get_json()
    session_id = data.get('sessionId')

    if not session_id:
        return jsonify({"message": "Session ID is required"}), 400

    try:
        # Hablamos con Stripe para obtener los detalles de la sesión de pago
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Verificamos que el pago fue realmente exitoso
        if checkout_session.payment_status == "paid":
            # (Aquí iría la lógica para guardar el pedido en la BD que haremos después)
            # Por ahora, solo confirmamos que funciona
            print(f"Payment successful for session: {session_id}")
            
            # Limpiamos el carrito de la sesión de Flask
            session.pop('cart', None)
            
            return jsonify({"message": "Purchase verified successfully"}), 200
        else:
            return jsonify({"message": "Payment not successful"}), 402 # 402 Payment Required

    except Exception as e:
        return jsonify(error=str(e)), 500
# =================================================================
# SECTION 6: SERVER STARTUP
# =================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)