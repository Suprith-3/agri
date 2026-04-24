from . import db

class GovernmentScheme(db.Model):
    """Model for storing government agricultural schemes."""
    __tablename__ = 'government_schemes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ministry = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    benefits = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text, nullable=False)
    documents = db.Column(db.Text, nullable=False)
    apply_link = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    is_state_specific = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(100), nullable=True)
    launch_year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<GovernmentScheme {self.name}>'

class SchemeApplication(db.Model):
    """Model for storing farmer's applications to schemes."""
    __tablename__ = 'scheme_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheme_id = db.Column(db.Integer, db.ForeignKey('government_schemes.id'), nullable=False)
    applicant_name = db.Column(db.String(255), nullable=False)
    aadhaar_number = db.Column(db.String(12), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    scheme = db.relationship('GovernmentScheme', backref=db.backref('applications', lazy=True))
    user = db.relationship('User', backref=db.backref('scheme_applications', lazy=True))

    def __repr__(self):
        return f'<SchemeApplication {self.id} for {self.scheme_id}>'
