from flask import Blueprint, jsonify, request, session, current_app
import stripe

from ..extensions import db
from ..models import Product, Order
from .. import api_login_required
from ..services.order_service import OrderService

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/create-checkout-session', methods=['POST'])
@api_login_required
def create_checkout_session():
    data = request.get_json()
    cart_items = data.get('cartItems') # Expects a list of {'id': product_id, 'quantity': ...}

    if not cart_items:
        return jsonify({"message": "Cart items are missing"}), 400

    line_items = []
    try:
        for item in cart_items:
            product = Product.query.get(item['id'])
            if not product:
                return jsonify({"message": f"Product with id {item['id']} not found."}), 404
            if product.stock < item['quantity']:
                return jsonify({"message": f"Insufficient stock for {product.name}. Only {product.stock} left."}), 400

            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                        # Pass product ID in metadata for reliable lookup on webhook/verification
                        'metadata': {'product_id': product.id}
                    },
                    'unit_amount': int(product.price * 100), # Use server-side price
                },
                'quantity': item['quantity'],
            })
    except (KeyError, TypeError):
        return jsonify({"message": "Invalid cart item format. Expected {'id': ..., 'quantity': ...}"}), 400

    frontend_domain = current_app.config['CORS_ORIGINS'].split(',')[0]

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{frontend_domain}/order/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_domain}/order/cancel",
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        current_app.logger.error(f"Stripe session creation failed: {e}")
        return jsonify(error=str(e)), 500

@orders_bp.route('/order/verify', methods=['POST'])
@api_login_required
def verify_order():
    data = request.get_json()
    session_id = data.get('sessionId')
    shipping_address_data = data.get('shippingAddress') # Get address from request body
    user_id = session.get('user_id')

    if not all([session_id, user_id, shipping_address_data]):
        return jsonify({"message": "Critical information (sessionId, userId, or shippingAddress) is missing"}), 400

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id, expand=["line_items.data.price.product"])
        if checkout_session.payment_status != "paid":
            return jsonify({"message": "Payment not successful according to Stripe"}), 402

        address = OrderService.create_address(shipping_address_data)
        order = OrderService.create_order(user_id, checkout_session.amount_total / 100.0, address.id)
        OrderService.update_user_phone(user_id, shipping_address_data.get('phoneNumber'))
        OrderService.process_line_items(order, checkout_session.line_items.data)

        db.session.commit()
        return jsonify({"message": "Purchase verified and order saved successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Order verification failed due to value error: {e}")
        return jsonify(error=str(e)), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"An unexpected error occurred during order verification: {e}")
        return jsonify(error="An internal error occurred. Please try again."), 500

@orders_bp.route('/my-orders', methods=['GET'])
@api_login_required
def get_my_orders():
    user_id = session.get('user_id')
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.date.desc()).all()

    orders_list = []
    for order in user_orders:
        address = order.address
        shipping_info = {
            'fullName': address.full_name,
            'streetAddress': address.street_address,
            'apartmentSuite': address.apartment_suite,
            'city': address.city,
            'postalCode': address.postal_code,
            'country': address.country,
            'phoneNumber': address.phone_number
        }
        order_data = {
            'id': order.id,
            'date': order.date.strftime('%Y-%m-%d %H:%M'),
            'total': order.total,
            'shippingInfo': shipping_info,
            'products': [{
                'name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price
            } for item in order.products]
        }
        orders_list.append(order_data)

    return jsonify(orders_list), 200
