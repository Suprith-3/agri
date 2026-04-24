from flask import Blueprint

# We will initialize all blueprints here

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
disease_bp = Blueprint('disease', __name__, url_prefix='/disease')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')
prediction_bp = Blueprint('prediction', __name__, url_prefix='/prediction')
recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/recommendation')
marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')
schemes_bp = Blueprint('schemes', __name__, url_prefix='/schemes')
