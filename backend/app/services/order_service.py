from ..extensions import db
from ..models import Address, Order, OrderProduct, Product, User

class OrderService:
    @staticmethod
    def create_address(address_data):
        """Creates and returns a new address."""
        address = Address(
            full_name=address_data['fullName'],
            street_address=address_data['streetAddress'],
            apartment_suite=address_data.get('apartmentSuite'),
            city=address_data['city'],
            postal_code=address_data['postalCode'],
            country=address_data['country'],
            phone_number=address_data.get('phoneNumber')
        )
        db.session.add(address)
        db.session.flush()
        return address

    @staticmethod
    def create_order(user_id, total, address_id):
        """Creates and returns a new order."""
        order = Order(user_id=user_id, total=total, address_id=address_id)
        db.session.add(order)
        return order

    @staticmethod
    def process_line_items(order, line_items):
        """Processes line items from a Stripe session, creates order-product links, and updates stock."""
        for item in line_items:
            product_id = item.price.product.metadata.get('product_id')
            if not product_id:
                # This should not happen if we set metadata correctly
                raise ValueError(f"Missing product_id in metadata for Stripe product {item.price.product.id}")

            product = Product.query.get(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found in database.")

            # Final stock check to prevent race conditions
            if product.stock < item.quantity:
                raise ValueError(f"Insufficient stock for product '{product.name}'.")

            order_product = OrderProduct(
                order=order,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=item.price.unit_amount / 100.0
            )
            db.session.add(order_product)
            product.stock -= item.quantity

    @staticmethod
    def update_user_phone(user_id, phone_number):
        """Updates the user's phone number if it is not already set."""
        if not phone_number:
            return
        user = User.query.get(user_id)
        if user and not user.phone_number:
            user.phone_number = phone_number
