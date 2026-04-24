import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Flask application configuration class."""
    
    # Core Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key-12345')
    
    # Database Config
    # Default to an absolute path for SQLite to avoid OperationalError
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    default_db_url = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'agri.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default_db_url)
    
    # 1. FIX: Render/SQLAlchemy 1.4+ postgres:// -> postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    # 2. RESILIENCE: Fallback to Local SQLite if Cloud DNS fails
    def check_cloud_alive(url):
        if not url or 'postgresql' not in url: return True
        try:
            import socket
            # Fast DNS check with 1-second timeout
            host = url.split('@')[-1].split(':')[0].split('/')[0]
            socket.setdefaulttimeout(1.0)
            socket.gethostbyname(host)
            return True
        except:
            return False

    if not check_cloud_alive(SQLALCHEMY_DATABASE_URI):
        print("\n[DB RESILIENCE] Cloud DNS Unreachable. Bypassing 500 Error...")
        print("[DB RESILIENCE] Falling back to Local SQLite: database/agri.db")
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'agri.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Engine options for high-latency cloud connections (Supabase/Render)
    # Using NullPool for transaction poolers (port 6543) to avoid handshake hangs
    from sqlalchemy.pool import NullPool
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
    }
    
    # Only add psycopg2-specific connect_args if using PostgreSQL
    if SQLALCHEMY_DATABASE_URI and 'postgresql' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
            # Removed connect_timeout to fix "unexpected keyword argument" crash on Render/Python 3.14
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    
    # Mail Config (for OTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    
    # AI API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # File Upload Config
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # Ensure directories exist
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'database'), exist_ok=True)
    except OSError:
        pass
