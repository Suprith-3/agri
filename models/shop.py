from . import db
from datetime import datetime

class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    gst_number = db.Column(db.String(50), unique=True, nullable=True)
    partner_name = db.Column(db.String(150), nullable=True)
    partner_details = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)

class Product(db.Model):
    __tablename__ = 'shop_products'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100)) # Fertilizer, Seeds, etc.
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    min_threshold = db.Column(db.Integer, default=20)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    supplier_name = db.Column(db.String(150))
    supplier_contact = db.Column(db.String(100))
    image = db.Column(db.String(255)) # Store the filename
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'min_threshold': self.min_threshold
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('shop_products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Float, nullable=False)

class AutoOrder(db.Model):
    __tablename__ = 'auto_orders'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('shop_products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Confirmed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ShopNotification(db.Model):
    __tablename__ = 'shop_notifications'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CustomerOrder(db.Model):
    __tablename__ = 'customer_orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Confirmed, Shipped, Delivered
    payment_method = db.Column(db.String(20)) # COD, Online
    payment_status = db.Column(db.String(20), default='Unpaid') # Paid, Unpaid
    razorpay_order_id = db.Column(db.String(100))
    tracking_id = db.Column(db.String(50), nullable=True, unique=True)
    address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('CustomerOrderItem', backref='order', lazy=True)

class CustomerOrderItem(db.Model):
    __tablename__ = 'customer_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('shop_products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
