from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from flask_session import Session

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__, template_folder="templates")
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

# Tables
class Resto(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), unique = False, nullable = False)
    strasse = db.Column(db.String(20), unique = True, nullable = False)
    plz = db.Column(db.Integer(), unique = False, nullable = False)
    beschreibung = db.Column(db.String(555), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    openTime = db.Column(db.String(), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=200)

class Kunde(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    vorname = db.Column(db.String(20), unique = False, nullable = False)
    nachname = db.Column(db.String(20), unique = False, nullable = False)
    adresse = db.Column(db.String(20), unique = False, nullable = False)
    postleitzahl = db.Column(db.Integer(), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=200)

class User:
    def __init__(self, id, type):
        self.id = id
        self.type = type

app.secret_key = "please end my suffering"

@app.route("/")
def index():
    if not session.get("user"):
        return render_template("index.html")
    user = session["user"]
    return redirect(url_for("homepage"))
        # Homepage Restaurantübersicht

# pop up request
@app.route("/registerKunde", methods=["POST"])
def registerKunde():
    if request.method == "POST":
        vorname = request.form.get("vorname")
        nachname = request.form.get("nachname")
        adresse = request.form.get("adresse")
        postleitzahl = request.form.get("postleitzahl")
        password = request.form.get("password")
        # create Kunde
        new_user = Kunde(
            vorname=vorname,
            nachname=nachname,
            adresse=adresse,
            postleitzahl=int(postleitzahl),
            password=password)
        print(f"Received: {vorname}, {nachname}, {adresse}, {postleitzahl}, {password}")
        db.session.add(new_user)
        db.session.commit()
        # todo replace user with primary key
        user = vorname
        session["user"] = user
        session["usertype"] = "Kunde"
    return render_template("index.html")

@app.route("/registerResto", methods=["POST"])
def registerResto():
    if request.method == "POST":
        name = request.form.get("name")
        strasse = request.form.get("strasse")
        plz = request.form.get("plz")
        beschreibung = request.form.get("beschreibung")
        password = request.form.get("password")
        openTime = request.form.get("openTime")

        new_resto = Resto(
            name=name,
            strasse=strasse,
            plz=int(plz),
            beschreibung=beschreibung,
            password=password,
            openTime=openTime)
        print(f"Received: {name}, {strasse}, {plz}, {beschreibung}, {password}, {openTime}")
        db.session.add(new_resto)
        db.session.commit()
        # to do replace with primary key / possible to get primary key from commit?
        user = name
        print(user)
        session["user"] = user
        print(session["user"])
        session["usertype"] = "Resto"
    return render_template("index.html")

@app.route("/profile/")
def profile():
    if not session.get("user"):
        return redirect(url_for("login"))
    user = session["user"]
    for kunde in db.session.query(Kunde).filter_by(vorname = user):
        print(kunde)
        user2 = getattr(kunde, "vorname")
    print(user2)
    return render_template("profile.html", content=[user+".name", user+".address", "blbllb", "wifbwb"])
    # todo replace "content" with database results
    
    
@app.route("/profile/update/", methods=["POST", "GET"])
def profile_update():
    if not "user" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("profile_update.html")
    elif request.method == "POST":
        new_username = request.form["new_username"]
        session["user"] = new_username
        # todo insert user in database
        return redirect(url_for("profile"))
    else:
        return redirect(url_for("index"))
        # error message?

    

@app.route("/login/", methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user = request.form["username"]
        session["user"] = user
        return redirect(url_for("profile"))
    else:
        return redirect(url_for("index"))
        # error message?
        
@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# todo delete this
@app.route("/homepage/")
def homepage():
    if not "user" in session:
        return render_template("index_old.html")
    user = session["user"]
    return render_template("index_old.html", username = user)

@app.route("/summary/")
def summary():
    if not "user" in session:
        return redirect(url_for("login"))
    # get items from session cache
    selectedItems = []
    # query to get all item details for items
    return render_template("summary.html", selectedItems)


if __name__ == "__main__":
    # Create all tables within the application context
    with app.app_context():
        db.create_all()
        print(Kunde.query.all())
        print(Resto.query.all())

    print("Database tables created!")
    app.run(debug=True)
