from flask import Flask, jsonify, redirect, send_file, request, render_template, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime as dt
import os
import ast
import json

# My module imports
from forms import Register, Login
from database import Users, Keys, Cities, db, States
from data import DfWorker


# --------------------------------------- APP CONFIG -------------------------------------------------------------------
def config_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI")
    app.config["SECRET_KEY"] = os.environ.get("APP_KEY")
    Bootstrap5(app)
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    return app, login_manager


app, login_manager = config_app()

with app.app_context():
    db.create_all()


# define how to retrieve user from database for our login-manager
@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()


# ----------------------------------------------------- VIEW FUNCTIONS -------------------------------------------------
@app.route("/", methods=["POST", "GET"])
def index():
    date = dt.now().strftime("%B %Y")
    return render_template("index.html", date=date)


@app.route("/login", methods=["POST", "GET"])
def login():
    login_form = Login()
    if login_form.validate_on_submit():
        email = login_form.email.data
        if db.session.execute(db.Select(Users).where(Users.email == email)):
            user = db.session.execute(db.Select(Users).where(Users.email == email)).scalar()
            if check_password_hash(password=login_form.password.data, pwhash=user.password):
                login_user(user)
                return redirect(url_for("user_home"))
    return render_template("login-register.html", form=login_form, status="Login")


@app.route("/register", methods=["POST", "GET"])
def register():
    register_form = Register()
    if register_form.validate_on_submit():
        email = register_form.email.data
        name = register_form.name.data
        password = generate_password_hash(password=register_form.password.data, method="scrypt", salt_length=8)
        new_user = Users(email=email, name=name, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("user_home"))

    return render_template("login-register.html", form=register_form, status="Register")


@app.route("/user-home")
@login_required
def user_home():
    return render_template("states.html")


@app.route("/state-analytics", methods=["GET"])
@login_required
def state_home():
    state = request.args.get("state")

    # set default values for each http parameter
    default_params = {
        'state': state,
        'town': None,
        "scope": 'state',
        "sort_by": "a|price per square foot",
        "page": 0,
        "graph_state": "heatmap",
    }
    # create dictionary that has either the param in request or default value if not in request
    params = {param: request.args.get(param, default) for param, default in default_params.items()}

    # identify if the scope is town or state, acquire the properties respectively
    if params['scope'] == 'town':
        town = request.args.get("town").title()
        params['town'] = town
        print(params['town'])
        city = db.session.execute(db.Select(Cities).where(Cities.city == params['town'], Cities.state == params['state'])).scalar()
        if city:
            props = json.loads(city.json)
        else:
            props = None
    else:
        cities = {city.city: json.loads(city.json) for city in
                  db.session.execute(db.select(States).where(States.name == state)).scalar().cities}
        props = []
        for city in cities.values():
            for data in city:
                props.append(data)

    if props:
        dw = DfWorker(props)
        dw.dropna_inf()

        sort_direction, sort_on = params['sort_by'].split("|")
        if sort_direction == 'a':
            props = json.loads(dw.sort_ascending(by=sort_on))
        else:
            props = json.loads(dw.sort_descending(by=sort_on))

        dw.remove_outliers()

        if params['graph_state'] == 'heatmap':
            graph = dw.heatmap()
        else:
            graph = dw.scatter()

        return render_template("state_template.html",
                               graph=graph.to_html(include_plotlyjs='cdn'), props=props, state=params['state'],
                               town=params['town'], graph_state=params['graph_state'], sort_by=params['sort_by'],
                               scope=params['scope'], page=params['page'])
    else:
        flash(f"the location {params['town']}, {state} does not exist in database. Redirected to home page for {state}")
        return redirect( url_for("state_home", state=params['state']))




@app.route("/individual-prop")
def show_prop():
    photos = [ast.literal_eval(photo) for photo in request.args.getlist("photos")]
    return render_template("individual-prop.html", photos=photos)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
