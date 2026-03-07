from flask import Flask, render_template, request, redirect, url_for
from forms import RSVPForm # Import forms.py

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

USERS = []
NEXT_ID = 1


# Home Page Route
@app.route("/")
def home():
    return render_template("home.html")




# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, port=3000)