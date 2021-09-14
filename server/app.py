import re
from flask import Flask, request, render_template, redirect, url_for, session, flash
from data_layer import add_multiple_campaigns, check_setup_status, insert_business, login_flow, product_controller, signup_flow, pull_id, get_markers, update_password, update_setup_status, update_stage
from datetime import datetime, timedelta

import os

#config = dotenv_values(".env")

app = Flask(__name__)
app.secret_key = 'tqNawvA4vuARSO5vb5YBh8Aymgn7SGLt'
app.permanent_session_lifetime = timedelta(
    minutes=60)  # adjust session time here


@app.route("/", methods=['GET'])
def home():
    if "username" in session:
        return render_template('home_authenticated.html')
    else:
        return render_template('home.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """
    TODO: 
    """
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if len(username) < 6:
            error = "Username must be a minimum of 6 characters"
        elif len(password) < 10:
            error = "Password must be a minimum of 10 characters"
        else:
            if signup_flow(username, password) == True:
                return redirect(url_for("login"))
            else:
                error = "User already exists"

    return render_template('signup.html', error=error)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    TODO: None
    1. Check if user has setup their account, if not redirect them to the setup section
    """
    error = None
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        session["username"] = username

        if login_flow(username, password) == True:

            if check_setup_status(username) == False:

                print(username, "has logged in at", datetime.now())
                return redirect(url_for("setup"))
            else:
                return redirect(url_for("dashboard"))

        else:
            error = "Credentials Do Not Match"
            print(username, "Attempted to login at", datetime.now())
            return render_template("login.html", error=error)

    else:
        return render_template("login.html", error=error)


@app.route("/setup", methods=['GET', 'POST'])
def setup():
    error = None
    if request.method == 'GET':
        if "username" in session:
            username = session["username"]
            if check_setup_status(username) == True:
                return redirect(url_for("dashboard"))
            else:
                return render_template("name.html", error=error)
        else:
            return redirect(url_for("login"))


@app.route("/setup_name", methods=['POST'])
def setup_name():
    error = None
    if request.method == 'POST':
        if "username" in session:
            username = session["username"]
            UID = pull_id(username)
            business_name = request.form["business_name"]
            URL = request.form["URL"]
            if business_name == None or URL == None:
                flash("Please provide both the name of your business and URL")
            else:
                if insert_business(username, business_name, URL) == True:
                    update_stage(username, "locations")
                    return redirect(url_for("locations"))
                else:

                    return render_template("name.html", error=error)
        else:
            return redirect(url_for("login"))


@app.route("/locations", methods=['GET'])
def locations():
    error = None
    if request.method == 'GET':
        if "username" in session:
            username = session["username"]
            if check_setup_status(username) == True:
                return redirect(url_for("dashboard"))
            else:
                return render_template("locations.html", error=error)
        else:
            return redirect(url_for("login"))


@app.route("/add_locations", methods=['POST'])
def add_locations():
    """
    """
    error = None
    if request.method == 'POST':
        if "username" in session:
            username = session["username"]
            UID = pull_id(username)
            locations = request.form.get("locations")

            if locations == "":
                flash("You must provide at least one city")
                return render_template("locations.html", error=error)
            else:
                add_multiple_campaigns(UID, locations)
                flash("Adding campaigns...")
                update_stage(username, "products")
                return redirect(url_for("products"))

        else:
            return redirect(url_for("login"))


@app.route("/products", methods=['GET'])
def products():
    error = None
    if "username" in session:
        username = session["username"]

        if check_setup_status(username) == True:
            return redirect(url_for("dashboard"))
        else:
            return render_template("products.html", error=error)
    else:
        return redirect(url_for("login"))


@app.route("/add_products", methods=['POST'])
def add_products():
    """
    """
    error = None
    if "username" in session:
        username = session["username"]
        UID = pull_id(username)
        raw_products = request.form["products"]
        if raw_products == "":
            flash("You must provide at least one product to advertise")
            return render_template("products.html", error=error)
        else:

            if product_controller(UID, raw_products) == True:

                update_setup_status(username)
                update_stage(username, "dashboard")
                return redirect(url_for("dashboard"))
            else:
                error = "Something went wrong"
                return render_template("products.html", error=error)

    else:
        return redirect(url_for("login"))


@app.route("/dashboard", methods=['GET'])
def dashboard():
    if "username" in session:
        username = session["username"]
        buffer_list = get_markers(username)
        location_list = ""

        if len(buffer_list) == 1:
            location_list = buffer_list[0]
        else:
            for i in buffer_list:
                location_list += i + ','
        return render_template("dashboard.html", username=username, location_list=location_list)
    else:
        return redirect(url_for("login"))


@app.route('/update_locations',methods=['POST'])
def update_locations():
    if "username" in session:
        username = session["username"]
        updated_locations = request.form.get("location_list")
        return redirect(url_for("dashboard"))


@app.route('/update_products',methods=['POST'])
def update_products():
    if "username" in session:
        username = session["username"]
        updated_products = request.form.get("update_products")
        return redirect(url_for("dashboard"))



@app.route("/account", methods=['GET', 'POST'])
def account():
    if "username" in session:
        username = session["username"]
        return render_template("account.html", username=username)
    else:
        return redirect(url_for("login"))


@app.route("/change_password", methods=['POST'])
def change_password():
    error = None
    if "username" in session:
        username = session["username"]

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if login_flow(username, current_password) == True:
            if new_password == confirm_password:
                if update_password(username, current_password, new_password) == True:

                    flash('Password updated successfully!')
                    return redirect(url_for("dashboard"))
        else:
            flash('You need to provide the correct password!')
            return redirect(url_for("account"))

        return render_template("account.html", username=username)

    else:
        return redirect(url_for("login"))



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
