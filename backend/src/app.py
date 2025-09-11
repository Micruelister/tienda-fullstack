# =================================================================
# SECTION 1: IMPORTS
# =================================================================
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
import stripe
import os
from werkzeug.utils import secure_filename
import uuid
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import or_

# =================================================================
# SECTION 2: INITIAL CONFIGURATION
# =================================================================
app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)
load_dotenv()

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Session and Secret Key Configuration ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# --- Stripe Configuration ---
stripe.api_key = os.getenv('STRIPE_API_KEY')
YOUR_DOMAIN = 'http://127.0.0.1:5000'

# --- Upload Folder Configuration ---
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'static/uploads/products')

# --- Extension Initialization ---
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
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =================================================================
# SECTION 5: APPLICATION ROUTES
# =================================================================

# --- Main Page & API Routes ---
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products) 

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
            'imageUrl': url_for('static', filename='uploads/products/' + product.image_filename, _external=True) if product.image_filename else None
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
        'imageUrl': url_for('static', filename='uploads/products/' + product.image_filename, _external=True) if product.image_filename else None
    }
    return jsonify(product_data)

# --- User Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
# En app.py

@app.route('/api/login', methods=['POST']) # CAMBIO 1: Nueva ruta de API y solo POST
def api_login(): # CAMBIO 2: Nuevo nombre de función
    data = request.get_json() # CAMBIO 3: Leemos datos JSON, no de formulario
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    login_identity = data.get('email') # CAMBIO 4: Usamos .get() para leer del JSON
    password = data.get('password')

    if not login_identity or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter(or_(User.username == login_identity, User.email == login_identity)).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        
        # Enviamos una respuesta JSON exitosa
        return jsonify({
            "message": "Login successful!",
            "user": { "id": user.id, "username": user.username, "is_admin": user.is_admin }
        }), 200
    else:
        # Enviamos una respuesta JSON de error
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('cart', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# --- Product Detail Route (for Flask templates) ---
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)
 
# --- Shopping Cart Routes ---
@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    id_str = str(product_id)
    cart[id_str] = cart.get(id_str, 0) + 1
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    if not cart:
        return render_template('cart.html', cart_items=[], total_price=0)
    cart_items = []
    total_price = 0
    for id_str, quantity in cart.items():
        product = Product.query.get(int(id_str))
        if product:
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    id_str = str(product_id)
    if id_str in cart:
        del cart[id_str]
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

# --- Checkout Routes ---
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('home'))
    
    cart_items = []
    total_price = 0
    for id_str, quantity in cart.items():
        product = Product.query.get(int(id_str))
        if product:
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    if request.method == 'POST':
        try:
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item['product'].name},
                        'unit_amount': int(item['product'].price * 100),
                    },
                    'quantity': item['quantity'],
                })
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=YOUR_DOMAIN + '/order/success',
                cancel_url=YOUR_DOMAIN + '/order/cancel',
            )
            session['shipping_address'] = request.form['address']
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return str(e)

    return render_template('checkout_page.html', cart_items=cart_items, total_price=total_price)

@app.route('/api/logout', methods=['POST']) # Nueva ruta específica para la API
def api_logout():
    session.pop('user_id', None)
    session.pop('cart', None)
    session.pop('is_admin', None)
    # En lugar de redirigir, devolvemos una respuesta JSON de éxito
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Username, email, and password are required"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Comprobamos si el usuario o el email ya existen
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409 # 409 Conflict
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201 # 201 Created

@app.route('/order/success')
def order_success():
    cart = session.get('cart', {})
    address = session.get('shipping_address', '')
    if not cart or not address:
        flash('There was a problem processing your order.', 'danger')
        return redirect(url_for('home'))
    
    cart_items = []
    total_price = 0
    for id_str, quantity in cart.items():
        product = Product.query.get(int(id_str))
        if product:
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({'product': product, 'quantity': quantity})

    new_order = Order(total=total_price, shipping_address=address, user_id=session['user_id'])
    db.session.add(new_order)
    for item in cart_items:
        order_product = OrderProduct(quantity=item['quantity'], unit_price=item['product'].price, order=new_order, product=item['product'])
        db.session.add(order_product)
    db.session.commit()
    
    session.pop('cart', None)
    session.pop('shipping_address', None)
    
    flash('Thank you for your purchase! Your order has been processed.', 'success')
    return redirect(url_for('home'))

@app.route('/order/cancel')
def order_cancel():
    flash('Payment was canceled. You can try again.', 'warning')
    return redirect(url_for('view_cart'))

# --- Admin Panel Routes ---
@app.route('/admin/inventory')
@login_required
def manage_inventory():
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    products = Product.query.all()
    return render_template('manage_inventory.html', products=products)

@app.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
def create_product():
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        product_name = request.form['name']
        product_price = request.form['price']
        product_stock = request.form['stock']
        saved_image = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                extension = os.path.splitext(file.filename)[1]
                unique_filename = str(uuid.uuid4()) + extension
                filename = secure_filename(unique_filename)
                upload_path = app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                save_path = os.path.join(upload_path, filename)
                file.save(save_path)
                saved_image = filename
        new_product = Product(name=product_name, price=float(product_price), stock=int(product_stock), image_filename=saved_image)
        db.session.add(new_product)
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('manage_inventory'))
    return render_template('create_product.html')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    product_to_edit = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product_to_edit.name = request.form['name']
        product_to_edit.price = float(request.form['price'])
        product_to_edit.stock = int(request.form['stock'])
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                old_image = product_to_edit.image_filename
                extension = os.path.splitext(file.filename)[1]
                unique_filename = str(uuid.uuid4()) + extension
                filename = secure_filename(unique_filename)
                upload_path = app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                save_path = os.path.join(upload_path, filename)
                file.save(save_path)
                product_to_edit.image_filename = filename
                if old_image:
                    try:
                        os.remove(os.path.join(upload_path, old_image))
                    except OSError as e:
                        flash(f'Error deleting old image file: {e}', 'danger')

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('manage_inventory'))
        
    return render_template('edit_product.html', product=product_to_edit)

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    product_to_delete = Product.query.get_or_404(product_id)
    if product_to_delete.image_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product_to_delete.image_filename))
        except OSError as e:
            flash(f'Error deleting image file: {e}', 'danger')
    db.session.delete(product_to_delete)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('manage_inventory'))

# --- User Account Routes ---
@app.route('/my-account')
@login_required
def my_account():
    user_id = session['user_id']
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.date.desc()).all()
    user = User.query.get(user_id)
    return render_template('my_account.html', orders=user_orders, user=user)

# =================================================================
# SECTION 6: SERVER STARTUP
# =================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)