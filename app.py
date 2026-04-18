from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# App Config
app.config["SECRET_KEY"] = "development-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storefront.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database Setup
db = SQLAlchemy(app)


# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Products Page
@app.route("/products")
def products():
    return render_template("products.html")

# Detailed Product Page
@app.route("/product/<int:id>")
def product_detail(id):
    return render_template("product_detail.html", id=id)

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