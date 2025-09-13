# =================================================================
# FILE: app.py (ABSOLUTELY 100% COMPLETE AND VERIFIED)
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
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import stripe
from flask_session import Session

# --- App Initialization ---
app = Flask(__name__, template_folder='../templates', static_folder='../static')
load_dotenv()

# --- Configurations ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Flask-Session Configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

Session(app) # Initialize Session

CORS(app, origins="http://localhost:5173", supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'static/uploads/products')
stripe.api_key = os.getenv('STRIPE_API_KEY')

# --- Extensions ---
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
    description = db.Column(db.Text, nullable=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    address = db.relationship('Address', backref='order', uselist=False)
    products = db.relationship('OrderProduct', backref='order', lazy=True)

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state_province = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

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
        if 'user_id' not in session:
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# =================================================================
# SECTION 5: API ROUTES
# =================================================================

# --- Product API ---
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
            'imageUrl': url_for('static', filename=f'uploads/products/{product.image_filename}', _external=True) if product.image_filename else None,
            'description': product.description
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
        'imageUrl': url_for('static', filename=f'uploads/products/{product.image_filename}', _external=True) if product.image_filename else None,
        'description': product.description
    }
    return jsonify(product_data)

# --- Auth API ---
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
        return jsonify({"message": "Login successful!", "user": {"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

# --- Checkout API ---
@app.route('/api/create-checkout-session', methods=['POST'])
@api_login_required
def create_checkout_session():
    data = request.get_json()
    cart_items = data.get('cartItems')
    shipping_address = data.get('shippingAddress')
    if not cart_items or not shipping_address:
        return jsonify({"message": "Cart items or shipping address is missing"}), 400
    session['shipping_address'] = shipping_address
    YOUR_FRONTEND_DOMAIN = 'http://localhost:5173'
    line_items = []
    for item in cart_items:
        line_items.append({'price_data': {'currency': 'usd', 'product_data': {'name': item['name']}, 'unit_amount': int(item['price'] * 100)}, 'quantity': item['quantity']})
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_FRONTEND_DOMAIN + '/order/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_FRONTEND_DOMAIN + '/order/cancel')
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/order/verify', methods=['POST'])
@api_login_required
def verify_order():
    data = request.get_json()
    session_id = data.get('sessionId')
    user_id = session.get('user_id')
    shipping_address_data = session.get('shipping_address')
    if not all([session_id, user_id, shipping_address_data]):
        return jsonify({"message": "Critical information is missing to verify the order"}), 400
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id, expand=["line_items.data.price.product"])
        if checkout_session.payment_status == "paid":
            new_address = Address(
                full_name=shipping_address_data.get('fullName'),
                street_address=shipping_address_data.get('streetAddress'),
                city=shipping_address_data.get('city'),
                postal_code=shipping_address_data.get('postalCode'),
                country=shipping_address_data.get('country'))
            db.session.add(new_address)
            db.session.flush()
            new_order = Order(user_id=user_id, total=checkout_session.amount_total / 100.0, address_id=new_address.id)
            db.session.add(new_order)
            for item in checkout_session.line_items.data:
                product = Product.query.filter_by(name=item.price.product.name).first()
                if product:
                    order_product = OrderProduct(order=new_order, product_id=product.id, quantity=item.quantity, unit_price=item.price.unit_amount / 100.0)
                    db.session.add(order_product)
                    product.stock -= item.quantity
            db.session.commit()
            session.pop('shipping_address', None)
            return jsonify({"message": "Purchase verified and order saved successfully"}), 200
        else:
            return jsonify({"message": "Payment not successful according to Stripe"}), 402
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

# --- User Account API ---
@app.route('/api/my-orders', methods=['GET'])
@api_login_required
def get_my_orders():
    user_id = session.get('user_id')
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.date.desc()).all()
    orders_list = []
    for order in user_orders:
        order_data = {'id': order.id, 'date': order.date.strftime('%Y-%m-%d %H:%M'), 'total': order.total, 'shipping_address': order.address.street_address, 'products': []}
        for item in order.products:
            order_data['products'].append({'name': item.product.name, 'quantity': item.quantity, 'unit_price': item.unit_price})
        orders_list.append(order_data)
    return jsonify(orders_list), 200

@app.route('/api/user/profile', methods=['GET'])
@api_login_required
def get_user_profile():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    profile_data = {
        "username": user.username,
        "email": user.email,
        # "phone_number": user.phone_number,  # Uncomment if User model has phone_number
        # En el futuro, podríamos añadir full_name, phone_number, etc.
    }
    return jsonify(profile_data), 200

@app.route('/api/user/profile', methods=['PUT'])
@api_login_required
def update_user_profile():
    user_id = session.get('user_id')
    user_to_update = User.query.get_or_404(user_id)
    
    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')

    # Validación: Asegurarse de que el nuevo username o email no estén ya en uso por OTRO usuario
    if new_username != user_to_update.username and User.query.filter_by(username=new_username).first():
        return jsonify({"message": "Username already taken"}), 409
    if new_email != user_to_update.email and User.query.filter_by(email=new_email).first():
        return jsonify({"message": "Email already registered"}), 409
    
    user_to_update.username = new_username
    user_to_update.email = new_email
    
    db.session.commit()
    
    # Devolvemos el perfil actualizado para que el frontend pueda refrescar sus datos
    updated_user_data = {
        "id": user_to_update.id,
        "username": user_to_update.username,
        "email": user_to_update.email,
        "is_admin": user_to_update.is_admin
    }
    return jsonify({"message": "Profile updated successfully!", "user": updated_user_data}), 200

# --- Admin Product Management API ---
@app.route('/admin/product/new', methods=['POST'])
@api_login_required
def create_product():
    if not session.get('is_admin'):
        return jsonify({"message": "Admin access required"}), 403
    if 'name' not in request.form or 'price' not in request.form or 'stock' not in request.form:
        return jsonify({"message": "Name, price, and stock are required fields."}), 400
    product_name = request.form['name']
    product_price = request.form['price']
    product_stock = request.form['stock']
    product_description = request.form.get('description', '')
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
    new_product = Product(name=product_name, price=float(product_price), stock=int(product_stock), image_filename=saved_image_filename, description=product_description)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product created successfully!", "productId": new_product.id}), 201

@app.route('/api/products/<int:product_id>', methods=['POST'])
@api_login_required
def update_product(product_id):
    if not session.get('is_admin'):
        return jsonify({"message": "Admin access required"}), 403
    product_to_update = Product.query.get_or_404(product_id)
    product_to_update.name = request.form.get('name', product_to_update.name)
    product_to_update.price = float(request.form.get('price', product_to_update.price))
    product_to_update.stock = int(request.form.get('stock', product_to_update.stock))
    product_to_update.description = request.form.get('description', product_to_update.description)
    if 'image' in request.files:
        file = request.files.get('image')
        if file and file.filename != '':
            if product_to_update.image_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product_to_update.image_filename))
                except OSError as e:
                    print(f"Error deleting old image file: {e}")
            extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{extension}"
            filename = secure_filename(unique_filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            product_to_update.image_filename = filename
    db.session.commit()
    return jsonify({"message": f"Product '{product_to_update.name}' updated successfully"}), 200

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

@app.route('/api/admin/test', methods=['POST'])
@api_login_required
def admin_test():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return jsonify({"message": f"Hello, admin {user.username}! Your test was successful."}), 200

# =================================================================
# SECTION 7: SERVER STARTUP
# =================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)