from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from config import Config
from models import db, User, Product, Order, OrderItem, CartItem
from forms import RegisterForm, LoginForm, ProductForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)

# Make csrf_token() available in all templates
app.jinja_env.globals['csrf_token'] = generate_csrf

# Initial products to database
with app.app_context():
    db.create_all()

    products = [
        Product(name="Keyboard", description="A reliable mechanical keyboard great for gaming and typing.", price=99.99, stock=10, image="keyboard.png"),
        Product(name="Mouse", description="Ergonomic wireless mouse with adjustable DPI settings.", price=49.99, stock=25, image="mouse.png"),
        Product(name="Monitor", description="27-inch Full HD monitor with ultra-thin bezels and vibrant colors.", price=199.99, stock=5, image="monitor.png"),
        Product(name="Laptop", description="Lightweight laptop with a fast processor and all-day battery life.", price=1999.99, stock=2, image="laptop.png"),
        Product(name="Keyboard Pro", description="Premium keyboard with RGB backlighting and tactile switches.", price=149.99, stock=10, image="keyboard.png"),
        Product(name="Silent Mouse", description="Whisper-quiet mouse perfect for shared workspaces.", price=39.99, stock=0, image="mouse.png"),
        Product(name="Curved Monitor", description="32-inch curved display for an immersive viewing experience.", price=299.99, stock=5, image="monitor.png"),
        Product(name="Budget Laptop", description="Affordable laptop ideal for everyday tasks and web browsing.", price=999.99, stock=2, image="laptop.png"),
        Product(name="Compact Keyboard", description="Tenkeyless layout keyboard saving desk space without sacrificing function.", price=79.99, stock=10, image="keyboard.png"),
        Product(name="Gaming Mouse", description="High-precision gaming mouse with programmable buttons.", price=69.99, stock=5, image="mouse.png"),
        Product(name="4K Monitor", description="Crystal-clear 4K resolution monitor for creators and professionals.", price=499.99, stock=0, image="monitor.png"),
        Product(name="Laptop Pro", description="High-performance laptop designed for developers and power users.", price=2999.99, stock=7, image="laptop.png"),
    ]

    for product in products:
        if not Product.query.filter_by(name=product.name).first():
            db.session.add(product)

    db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def manager_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "manager":
            abort(403)
        return f(*args, **kwargs)
    return decorated

def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "customer":
            abort(403)
        return f(*args, **kwargs)
    return decorated


# Routes

@app.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)


@app.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template("product_detail.html", product=product)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("register"))

        new_user = User(
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard") if user.role == "manager" else url_for("customer_dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# Cart and Checkout

@app.route("/cart")
@login_required
@customer_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
@customer_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock == 0:
        flash("Sorry, that product is out of stock.", "danger")
        return redirect(url_for("product_detail", id=product_id))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        if existing.quantity < product.stock:
            existing.quantity += 1
            flash(f"Updated quantity for {product.name}.", "success")
        else:
            flash("You've reached the available stock limit.", "danger")
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=product_id, quantity=1))
        flash(f"{product.name} added to cart!", "success")

    db.session.commit()
    return redirect(url_for("product_detail", id=product_id))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
@customer_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["POST"])
@login_required
@customer_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for("cart"))

    # Check stock first
    for item in items:
        if item.quantity > item.product.stock:
            flash(f"Not enough stock for {item.product.name}.", "danger")
            return redirect(url_for("cart"))

    total = sum(item.product.price * item.quantity for item in items)
    order = Order(user_id=current_user.id, total_price=round(total, 2))
    db.session.add(order)
    db.session.flush()  # get order.id

    for item in items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price,
            product_name=item.product.name
        ))
        item.product.stock -= item.quantity
        db.session.delete(item)

    db.session.commit()
    flash(f"Order #{order.id} placed successfully! Total: ${total:.2f}", "success")
    return redirect(url_for("customer_dashboard"))


# Customer Dashboard

@app.route("/customer-dashboard")
@login_required
@customer_required
def customer_dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("customer_dashboard.html", orders=orders)


# Admin Dashboard

@app.route("/admin-dashboard")
@login_required
@manager_required
def admin_dashboard():
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin_dashboard.html", products=products, orders=orders)


@app.route("/admin/product/add", methods=["GET", "POST"])
@login_required
@manager_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            image=form.image.data
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{product.name}' added.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("product_form.html", form=form, title="Add Product")


@app.route("/admin/product/edit/<int:id>", methods=["GET", "POST"])
@login_required
@manager_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.image = form.image.data
        db.session.commit()
        flash(f"Product '{product.name}' updated.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("product_form.html", form=form, title="Edit Product")


@app.route("/admin/product/delete/<int:id>", methods=["POST"])
@login_required
@manager_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash(f"Product '{product.name}' deleted.", "info")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin_email = "admin@bytesupply.com"
        if not User.query.filter_by(email=admin_email).first():
            db.session.add(User(
                email=admin_email,
                password_hash=generate_password_hash("Admin123"),
                role="manager"
            ))
            db.session.commit()
            print("Default manager created: admin@bytesupply.com / Admin123")

    app.run(debug=True)