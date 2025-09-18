from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
session = Session()
csrf = CSRFProtect()
migrate = Migrate()
