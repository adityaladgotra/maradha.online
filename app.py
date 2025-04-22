import os
import logging
from extensions import db

from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with custom base


# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add template filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s:
        return s.replace('\n', '<br>')
    return ''

# Configure database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    database_url = "sqlite:///maradha.db"
    logging.warning("DATABASE_URL not found, using SQLite database")

# Fix PostgreSQL URL format for SQLAlchemy 1.4+
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Print database URL for debugging (without showing password)
logging.info(f"Using database type: {'PostgreSQL' if 'postgresql://' in database_url else 'SQLite'}")

# Set up file upload configuration
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max upload

# Initialize the database
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# Create upload folder if it doesn't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

with app.app_context():
    # Import models and routes here to avoid circular imports
    from models import Admin, Student
    import routes  # noqa: F401
    
    # Recreate all database tables
    db.drop_all()
    db.create_all()
    
    # Create admin account if it doesn't exist
    admin = Admin.query.filter_by(username="maradha.online").first()
    if not admin:
        admin = Admin(username="maradha.online")
        admin.set_password("Maradha@123")
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin account created")

@login_manager.user_loader
def load_user(user_id):
    # The ID format will be "admin-123" or "student-123"
    if '-' not in user_id:
        return None
        
    user_type, user_id = user_id.split('-')
    
    from models import Admin, Student
    
    if user_type == 'admin':
        return Admin.query.get(int(user_id))
    elif user_type == 'student':
        return Student.query.get(int(user_id))
    
    return None
