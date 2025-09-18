import os
import click
from app import create_app, db
from app.models import User, Product, Order
from app.extensions import bcrypt

# Create the Flask app instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """
    Creates a shell context that adds the database instance and models
    to the shell session. This allows for convenient testing and debugging
    from the Flask shell.
    """
    return dict(db=db, User=User, Product=Product, Order=Order)

@app.cli.command('create-admin')
@click.argument('password')
def create_admin(password):
    """Creates a default admin user."""
    if User.query.filter_by(username='admin').first():
        print('Admin user "admin" already exists.')
        return

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    admin_user = User(username='admin', email='admin@example.com', password_hash=hashed_password, is_admin=True)
    db.session.add(admin_user)
    db.session.commit()
    print('Admin user "admin" created successfully.')

if __name__ == '__main__':
    # The application is run through the 'flask run' command,
    # which is configured by environment variables.
    # This block is for direct execution, e.g., `python run.py`.
    # For development, 'flask run' is preferred as it offers
    # better debugging and reloading capabilities.
    app.run(host='0.0.0.0', port=5000)
