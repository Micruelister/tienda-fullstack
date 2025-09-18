from flask import Blueprint, jsonify, request, session, current_app
import stripe

from ..extensions import db
from ..models import Product, Order, OrderProduct, Address, User
from .. import api_login_required

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/create-checkout-session', methods=['POST'])
@api_login_required
def create_checkout_session():
    data = request.get_json()
    cart_items = data.get('cartItems')
    shipping_address = data.get('shippingAddress')

    if not cart_items or not shipping_address:
        return jsonify({"message": "Cart items or shipping address is missing"}), 400

    session['shipping_address'] = shipping_address

    # Use the frontend domain from config
    frontend_domain = current_app.config['CORS_ORIGINS'].split(',')[0]

    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': item['quantity'],
        })

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
        return jsonify(error=str(e)), 500

@orders_bp.route('/order/verify', methods=['POST'])
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
            # Create and save the address
            new_address = Address(
                full_name=shipping_address_data['fullName'],
                street_address=shipping_address_data['streetAddress'],
                apartment_suite=shipping_address_data.get('apartmentSuite'),
                city=shipping_address_data['city'],
                postal_code=shipping_address_data['postalCode'],
                country=shipping_address_data['country'],
                phone_number=shipping_address_data.get('phoneNumber')
            )
            db.session.add(new_address)
            db.session.flush() # Flush to get the new_address.id

            # Create the order
            new_order = Order(
                user_id=user_id,
                total=checkout_session.amount_total / 100.0,
                address_id=new_address.id
            )
            db.session.add(new_order)

            # Update user's phone number if it's missing
            user = User.query.get(user_id)
            if user and not user.phone_number:
                user.phone_number = shipping_address_data.get('phoneNumber')

            # Create order-product associations and update stock
            for item in checkout_session.line_items.data:
                product = Product.query.filter_by(name=item.price.product.name).first()
                if product:
                    order_product = OrderProduct(
                        order=new_order,
                        product_id=product.id,
                        quantity=item.quantity,
                        unit_price=item.price.unit_amount / 100.0
                    )
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
