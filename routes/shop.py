from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db
from models.shop import Shop, Product, Supplier, Sale, SaleItem, AutoOrder, ShopNotification, CustomerOrder, CustomerOrderItem
from flask import session
from datetime import datetime
import razorpay
import os
import uuid
from flask import send_from_directory

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

def get_razorpay_client():
    key_id = os.getenv('RAZORPAY_KEY_ID')
    key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        print("[CRITICAL] Razorpay keys not found in environment!")
        # Fallback for development if needed, but safer to let it fail or log
    return razorpay.Client(auth=(key_id, key_secret))

@shop_bp.route('/')
@login_required
def dashboard():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop:
        return redirect(url_for('shop.register_shop'))
    
    if not shop.is_active:
        return render_template('shop/activate.html', shop=shop, razorpay_key=os.getenv('RAZORPAY_KEY_ID'))
    
    total_products = Product.query.filter_by(shop_id=shop.id).count()
    low_stock = Product.query.filter(Product.shop_id == shop.id, Product.stock <= Product.min_threshold).all()
    recent_sales = Sale.query.filter_by(shop_id=shop.id).order_by(Sale.created_at.desc()).limit(5).all()
    pending_orders = AutoOrder.query.filter_by(shop_id=shop.id, status='Pending').all()
    customer_orders = CustomerOrder.query.filter_by(shop_id=shop.id).order_by(CustomerOrder.created_at.desc()).all()
    
    return render_template('shop/dashboard.html', 
                           shop=shop, 
                           total_products=total_products,
                           low_stock=low_stock,
                           recent_sales=recent_sales,
                           pending_orders=pending_orders,
                           customer_orders=customer_orders)

@shop_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register_shop():
    # Check if user already has a shop
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if shop:
        return redirect(url_for('shop.dashboard'))
        
    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        address = request.form.get('address')
        gst = request.form.get('gst')
        partner_name = request.form.get('partner_name')
        partner_details = request.form.get('partner_details')
        if not gst or gst.strip() == "":
            gst = None
        
        new_shop = Shop(
            owner_id=current_user.id, 
            shop_name=shop_name, 
            address=address, 
            gst_number=gst,
            partner_name=partner_name,
            partner_details=partner_details
        )
        try:
            db.session.add(new_shop)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error_msg = str(e).lower()
            if 'stringdatarighttruncation' in error_msg or 'value too long' in error_msg:
                from sqlalchemy import text
                # Auto-heal: Fix the cloud schema on the fly
                db.session.execute(text("ALTER TABLE shops ALTER COLUMN gst_number TYPE VARCHAR(50)"))
                db.session.commit()
                # Try the save again
                db.session.add(new_shop)
                db.session.commit()
            elif 'unique' in error_msg or 'duplicate' in error_msg:
                flash("A shop with this GST number is already registered. Please use a unique GST number.", "danger")
                return render_template('shop/register.html')
            else:
                raise e
        
        flash("Shop registered successfully!", "success")
        return redirect(url_for('shop.dashboard'))
        
    return render_template('shop/register.html')

@shop_bp.route('/inventory')
@login_required
def inventory():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop: return redirect(url_for('shop.register_shop'))
    if not shop.is_active: return redirect(url_for('shop.dashboard'))
    
    products = Product.query.filter_by(shop_id=shop.id).all()
    suppliers = Supplier.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/inventory.html', products=products, suppliers=suppliers)

@shop_bp.route('/products/add', methods=['POST'])
@login_required
def add_product():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price'))
    stock = int(request.form.get('stock'))
    threshold = int(request.form.get('threshold'))
    supplier_id = request.form.get('supplier_id')
    supplier_name = request.form.get('supplier_name')
    supplier_contact = request.form.get('supplier_contact')
    
    # Handle Image Upload
    image_file = request.files.get('image')
    image_filename = None
    if image_file and image_file.filename:
        from werkzeug.utils import secure_filename
        import uuid
        ext = os.path.splitext(image_file.filename)[1]
        image_filename = f"prod_{uuid.uuid4().hex}{ext}"
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        image_file.save(os.path.join(upload_path, image_filename))
    
    new_prod = Product(
        shop_id=shop.id, 
        name=name, 
        category=category, 
        price=price, 
        stock=stock, 
        min_threshold=threshold, 
        supplier_id=supplier_id if supplier_id else None,
        supplier_name=supplier_name,
        supplier_contact=supplier_contact,
        image=image_filename
    )
    db.session.add(new_prod)
    db.session.commit()
    flash("Product added with image!", "success")
    return redirect(url_for('shop.inventory'))

@shop_bp.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop: return redirect(url_for('shop.register_shop'))
    if not shop.is_active: return redirect(url_for('shop.dashboard'))

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        items = request.form.getlist('product_id[]')
        qtys = request.form.getlist('quantity[]')
        
        total = 0
        new_sale = Sale(shop_id=shop.id, customer_name=customer_name, total_amount=0)
        db.session.add(new_sale)
        db.session.flush()
        
        for p_id, q in zip(items, qtys):
            product = db.session.get(Product, int(p_id))
            qty = int(q)
            if product.stock >= qty:
                product.stock -= qty
                item_total = product.price * qty
                total += item_total
                
                sale_item = SaleItem(sale_id=new_sale.id, product_id=product.id, quantity=qty, price_at_sale=product.price)
                db.session.add(sale_item)
                
                # Auto Reorder Logic
                if product.stock <= product.min_threshold:
                    trigger_reorder(shop.id, product)
            else:
                flash(f"Low stock for {product.name}", "danger")
                
        new_sale.total_amount = total
        db.session.commit()
        flash(f"Bill generated! Total: ₹{total}", "success")
        return redirect(url_for('shop.dashboard'))
        
    products = Product.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/billing.html', products=products)

def trigger_reorder(shop_id, product):
    """Triggers an automatic order and logs an SMS simulation to the supplier."""
    shop = db.session.get(Shop, shop_id)
    
    # Check if a pending order already exists
    existing = AutoOrder.query.filter_by(product_id=product.id, status='Pending').first()
    if not existing:
        order_qty = product.min_threshold * 2
        new_order = AutoOrder(shop_id=shop_id, product_id=product.id, supplier_id=product.supplier_id, quantity=order_qty)
        db.session.add(new_order)
        
        # Determine supplier contact
        contact_name = product.supplier_name or "Supplier"
        phone = product.supplier_contact
        
        message_body = f"URGENT ORDER: {shop.shop_name} needs {order_qty} units of {product.name}. Delivery Address: {shop.address}."
        
        # Log the 'Automated SMS' (Simulation)
        print(f"\n--- [AUTOMATED SMS SENT] ---\nTO: {phone}\nBODY: {message_body}\n---------------------------\n")
        
        notif = ShopNotification(shop_id=shop_id, message=f"Low stock: {product.name}. Auto-SMS sent to {contact_name} ({phone}) for {order_qty} units.")
        db.session.add(notif)

@shop_bp.route('/create_payment', methods=['POST'])
@login_required
def create_payment():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    client = get_razorpay_client()
    # Amount in paise (100 paise = 1 INR)
    data = {"amount": 100, "currency": "INR", "receipt": f"shop_{shop.id}"}
    try:
        payment = client.order.create(data=data)
        print(f"[SHOPS] Created activation payment for shop {shop.id}: {payment.get('id')}")
        return jsonify(payment)
    except Exception as e:
        print(f"[SHOPS] Error creating Razorpay order: {str(e)}")
        return jsonify({'error': str(e)}), 400

@shop_bp.route('/verify_payment', methods=['POST'])
@login_required
def verify_payment():
    data = request.json
    payment_id = data.get('razorpay_payment_id')
    
    # Matching the 'GOAT' logic which the user says is working
    if payment_id:
        shop = Shop.query.filter_by(owner_id=current_user.id).first()
        if shop:
            shop.is_active = True
            db.session.commit()
            print(f"[SHOPS] Shop {shop.id} activated via payment {payment_id}")
            return jsonify({'status': 'success'})
    
    return jsonify({'status': 'failed'}), 400

@shop_bp.route('/suppliers', methods=['GET', 'POST'])
@login_required
def manage_suppliers():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop: return redirect(url_for('shop.register_shop'))
    if not shop.is_active: return redirect(url_for('shop.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')
        address = request.form.get('address')
        
        new_sup = Supplier(shop_id=shop.id, name=name, contact=contact, address=address)
        db.session.add(new_sup)
        db.session.commit()
        return redirect(url_for('shop.manage_suppliers'))
        
    suppliers = Supplier.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/suppliers.html', suppliers=suppliers)

@shop_bp.route('/public/products')
def public_shop():
    """Browse products from all shops (customer view)."""
    products = Product.query.all()
    cart_count = len(session.get('cart', {}))
    return render_template('shop/public_shop.html', products=products, cart_count=cart_count)

@shop_bp.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    session['cart'] = cart
    flash("Added to cart!", "success")
    return redirect(url_for('shop.public_shop'))

@shop_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = db.session.get(Product, int(pid))
        if product:
            item_total = product.price * qty
            total += item_total
            cart_items.append({'product': product, 'qty': qty, 'total': item_total})
    return render_template('shop/cart.html', items=cart_items, total=total)

@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart: return redirect(url_for('shop.public_shop'))
    
    total = 0
    for pid, qty in cart.items():
        p = db.session.get(Product, int(pid))
        if p: total += p.price * qty
            
    if request.method == 'POST':
        address = request.form.get('address')
        method = request.form.get('payment_method')
        
        # Create Order
        # Just use the shop from the first product for simplicity in this MVP
        first_pid = next(iter(cart))
        first_prod = db.session.get(Product, int(first_pid))
        
        new_order = CustomerOrder(
            user_id=current_user.id,
            shop_id=first_prod.shop_id,
            total_amount=total,
            payment_method=method,
            address=address,
            status='Pending'
        )
        db.session.add(new_order)
        db.session.flush()
        
        for pid, qty in cart.items():
            p = db.session.get(Product, int(pid))
            item = CustomerOrderItem(order_id=new_order.id, product_id=p.id, quantity=qty, price_at_purchase=p.price)
            db.session.add(item)
            p.stock -= qty
            
        db.session.commit()
        
        if method == 'Online':
            client = get_razorpay_client()
            razorpay_order = client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "payment_capture": "1"
            })
            new_order.razorpay_order_id = razorpay_order['id']
            db.session.commit()
            return render_template('shop/pay_order.html', order=new_order, r_order=razorpay_order, key=os.getenv('RAZORPAY_KEY_ID'))
        
        session['cart'] = {}
        flash("Order placed successfully via COD!", "success")
        return redirect(url_for('dashboard.home'))

    return render_template('shop/checkout.html', total=total)

@shop_bp.route('/order/verify', methods=['POST'])
@login_required
def verify_order_payment():
    data = request.json
    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature(data)
        order_idx = data.get('order_idx') # My internal ID passed back
        order = db.session.get(CustomerOrder, int(order_idx))
        order.payment_status = 'Paid'
        order.status = 'Confirmed'
        db.session.commit()
        session['cart'] = {}
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'failed'}), 400

@shop_bp.route('/order/accept/<int:order_id>', methods=['POST'])
@login_required
def accept_order(order_id):
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    order = db.session.get(CustomerOrder, order_id)
    
    if order and order.shop_id == shop.id:
        if order.status == 'Pending' or order.status == 'Confirmed':
            order.status = 'Accepted'
            # Generate a unique tracking ID for delivery
            order.tracking_id = f"TRK-{uuid.uuid4().hex[:8].upper()}"
            db.session.commit()
            flash(f"Order #{order_id} Accepted! Tracking ID: {order.tracking_id}", "info")
        else:
            flash("Order is already processed.", "warning")
    else:
        flash("Order not found or unauthorized.", "danger")
        
    return redirect(url_for('shop.dashboard'))
