from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Product, Order
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Adds products to database for testing
with app.app_context():
    db.create_all()

    
    products = [
        Product(name="Keyboard", description="This is a placeholder description for the keyboard", price=99.99, stock=10, image="keyboard.png"),
        Product(name="Mouse", description="mouse", price=49.99, stock=25, image="mouse.png"),
        Product(name="Monitor", description="monitor", price=199.99, stock=5, image="monitor.png"),
        Product(name="Laptop", description="laptop", price=1999.99, stock=2, image="laptop.png"),

        Product(name="Keyboard2", description="This is a placeholder description for the keyboard", price=99.99, stock=10, image="keyboard.png"),
        Product(name="Mouse2", description="mouse", price=49.99, stock=0, image="mouse.png"),
        Product(name="Monitor2", description="monitor", price=199.99, stock=5, image="monitor.png"),
        Product(name="Laptop2", description="laptop", price=999.99, stock=2, image="laptop.png"),

        Product(name="Keyboard3", description="This is a placeholder description for the keyboard", price=99.99, stock=10, image="keyboard.png"),
        Product(name="Mouse3", description="mouse", price=49.99, stock=5, image="mouse.png"),
        Product(name="Monitor3", description="monitor", price=199.99, stock=0, image="monitor.png"),
        Product(name="Laptop3", description="laptop", price=2999.99, stock=7, image="laptop.png"),
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

def manager_required():
    if not current_user.is_authenticated or current_user.role != "manager":
        abort(403)

@app.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)

# Detailed Product Page
@app.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get(id)
    return render_template("product_detail.html", id=id, product=product)

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

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(
            email=form.email.data.lower(),
            password_hash=hashed_password,
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

            if user.role == "manager":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("customer_dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/customer-dashboard")
@login_required
def customer_dashboard():
    return render_template("customer_dashboard.html")

@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    manager_required()
    return render_template("admin_dashboard.html")

@app.errorhandler(403)
def forbidden(e):
    return "<h1>403 Forbidden</h1><p>You do not have access to this page.</p>", 403

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Optional: create a default manager account once
        admin_email = "admin@bytesupply.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password_hash=generate_password_hash("Admin123"),
                role="manager"
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default manager created:")
            print("Email: admin@bytesupply.com")
            print("Password: Admin123")

    app.run(debug=True)