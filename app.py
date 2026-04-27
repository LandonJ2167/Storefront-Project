from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Product, Order

app = Flask(__name__)

# App Config
app.config["SECRET_KEY"] = "development-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storefront.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database Setup
db.init_app(app)

with app.app_context():
    db.create_all()

    
    products = [
        Product(name="Keyboard", description="This is a placeholder description for the keyboard", price=99.99, stock=10),
        Product(name="Mouse", description="mouse", price=49.99, stock=25),
        Product(name="Monitor", description="monitor", price=199.99, stock=5),
        Product(name="Laptop", description="laptop", price=1999.99, stock=2),
    ]

    for product in products:
        if not Product.query.filter_by(name=product.name).first():
            db.session.add(product)

    db.session.commit()


# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Products Page
@app.route("/products")
def products():
    products = Product.query.all()
    return render_template("products.html", products=products)

# Detailed Product Page
@app.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get(id)
    return render_template("product_detail.html", id=id, product=product)

# Register
@app.route("/register")
def register():
    return render_template("register.html")

# Login
@app.route("/login")
def login():
    return render_template("login.html")



# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, port=3000)