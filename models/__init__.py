from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# This file just initializes the db object and eventually 
# could import all models to ensure they are registered.
