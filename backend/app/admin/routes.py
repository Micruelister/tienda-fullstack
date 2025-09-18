import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Product, ProductImage, Order, User
from .. import admin_required

admin_bp = Blueprint('admin_bp', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_product_images(files, product_id):
    """Helper function to save product images."""
    images_to_add = []
    for file in files:
        if file and file.filename != '' and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{extension}"
            filename = secure_filename(unique_filename)

            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            images_to_add.append(ProductImage(filename=filename, product_id=product_id))
    return images_to_add

@admin_bp.route('/product/new', methods=['POST'])
@admin_required
def create_product():
    if 'name' not in request.form or 'price' not in request.form or 'stock' not in request.form:
        return jsonify({"message": "Name, price, and stock are required fields."}), 400

    new_product = Product(
        name=request.form['name'],
        price=float(request.form['price']),
        stock=int(request.form['stock']),
        description=request.form.get('description', ''),
        brand=request.form.get('brand', '')
    )
    db.session.add(new_product)
    db.session.flush()

    new_images = save_product_images(request.files.getlist('images'), new_product.id)
    if new_images:
        db.session.add_all(new_images)

    db.session.commit()
    return jsonify({"message": "Product created successfully!", "productId": new_product.id}), 201

@admin_bp.route('/products/<int:product_id>', methods=['POST'])
@admin_required
def update_product(product_id):
    product_to_update = Product.query.get_or_404(product_id)

    product_to_update.name = request.form.get('name', product_to_update.name)
    product_to_update.price = float(request.form.get('price', product_to_update.price))
    product_to_update.stock = int(request.form.get('stock', product_to_update.stock))
    product_to_update.description = request.form.get('description', product_to_update.description)
    product_to_update.brand = request.form.get('brand', product_to_update.brand)

    new_images = save_product_images(request.files.getlist('images'), product_to_update.id)
    if new_images:
        db.session.add_all(new_images)

    db.session.commit()
    return jsonify({"message": f"Product '{product_to_update.name}' updated successfully"}), 200

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    product_to_delete = Product.query.get_or_404(product_id)

    for image in product_to_delete.images:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename))
        except OSError as e:
            current_app.logger.error(f"Error deleting image file {image.filename}: {e}")

    db.session.delete(product_to_delete)
    db.session.commit()
    return jsonify({"message": f"Product '{product_to_delete.name}' deleted successfully"}), 200

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    orders = Order.query.order_by(Order.date.desc()).all()
    orders_list = []
    for order in orders:
        user = User.query.get(order.user_id)
        order_data = {
            'id': order.id,
            'date': order.date.strftime('%Y-%m-%d %H:%M'),
            'total': order.total,
            'customer_name': user.username if user else 'Unknown',
            'shipping_info': {
                'full_name': order.address.full_name,
                'address': order.address.street_address,
                'apartment_suite': order.address.apartment_suite,
                'city': order.address.city,
                'country': order.address.country,
                'postal_code': order.address.postal_code,
                'phoneNumber': order.address.phone_number
            },
            'products': [{
                'name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price
            } for item in order.products]
        }
        orders_list.append(order_data)

    return jsonify(orders_list), 200

@admin_bp.route('/test', methods=['POST'])
@admin_required
def admin_test():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return jsonify({"message": f"Hello, admin {user.username}! Your test was successful."}), 200
