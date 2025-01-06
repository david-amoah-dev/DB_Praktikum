from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__, template_folder="templates")
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


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
        id = 1
        user = {"id": id, "type": "Kunde"}
        session["user"] = user
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
        id = 1
        user = {"id": id, "type": "Resto"}
        session["user"] = user
    return render_template("index.html")

@app.route("/profile/")
def profile():
    if not session.get("user"):
        return redirect(url_for("login"))
    user1 = session["user"]
    print(user1)
    user2 = None
    if user1["type"] == "Kunde":
        for kunde in db.session.query(Kunde).filter_by(id = user1["id"]):
            user2 = getattr(kunde, "name")
    else:
        for resto in db.session.query(Resto).filter_by(id = user1["id"]):
            user2 = getattr(resto, "name")
    print(user2)
    return render_template("profile.html", content=user2, userType = user1["type"])
    # todo update in profile html to deal with kunde type
    
    
@app.route("/profile/update/", methods=["POST", "GET"])
def profile_update():
    user = session["user"]
    if user["type"] == "Kunde":
        if request.method == "POST":
            name = request.form.get("name")
            strasse = request.form.get("strasse")
            plz = request.form.get("plz")
            beschreibung = request.form.get("beschreibung")
            password = request.form.get("password")
            
    else: 
        if request.method == "POST":
            name = request.form.get("name")
            strasse = request.form.get("strasse")
            plz = request.form.get("plz")
            beschreibung = request.form.get("beschreibung")
            password = request.form.get("password")
            openTime = request.form.get("openTime")

        # update user

    return redirect(url_for("profile"))

    

    
# delete this
@app.route("/login/", methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        temp = request.form["username"]
        user1 = {"id" : 1, "type" : "Kunde"}
        session["user"] = user1
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
    # only test
    item1 = {"name" : "Name1", "description" : "Text1", "price" : 1.20, "amount" : 5}
    item2 = {"name" : "Name2", "description" : "Text2", "price" : 2.20, "amount" : 4}
    item3 = {"name" : "Name3", "description" : "Text3", "price" : 3.20, "amount" : 3}
    
    #if not "items" in session:
        # no items selected
    #    return redirect(url_for("index"))
    items = [item1, item2, item3]
    total = 0.0
    for e in items:
        total += e["price"]
    final = f"{total:.2f}"
    return render_template("summary.html", content = items, total = final)

@app.route("/profile_alternative/", methods=["GET", "POST"])
def profile_alternative():
    if not "user" in session:
        return redirect(url_for("login"))
    user1 = session["user"]
    if request.method == "GET":
        if user1["type"] == "Kunde":
            for kunde in db.session.query(Kunde).filter_by(id = user1["id"]):
                content = {
                    "vorname" : getattr(kunde, "vorname"),
                    "nachname" : getattr(kunde, "nachname"),
                    "adresse" : getattr(kunde, "adresse"),
                    "postleitzahl" : getattr(kunde, "postleitzahl"),
                    "password" : getattr(kunde, "password")
                    }
        else:
            for resto in db.session.query(Resto).filter_by(id = user1["id"]):
                content = { 
                    "name" : getattr(kunde, "name"),
                    "strasse" : getattr(kunde, "strasse"),
                    "plz" : getattr(kunde, "plz"),
                    "beschreibung" : getattr(kunde, "beschreibung"),
                    "password" : getattr(kunde, "password"),
                    "openTime" : getattr(kunde, "openTime")
                    }
        return render_template("profile_alternative.html", content = content, user1 = user1)
    elif request.method == "POST":
        if user1["type"] == "Kunde":
            for user2 in db.session.query(Kunde).filter_by(id = user1["id"]):
                print(user2)
                if request.form.get("vorname"):
                    user2.vorname = request.form.get("vorname")
                if request.form.get("nachname"):
                    user2.nachname = request.form.get("nachname")
                if request.form.get("adresse"):
                    user2.adresse = request.form.get("adresse")
                if request.form.get("postleitzahl"):
                    user2.postleitzahl = request.form.get("postleitzahl")
                if request.form.get("password"):
                    user2.password = request.form.get("password")
                db.session.commit()
                return redirect(url_for("profile_alternative"))
        else:
            name = request.form.get("name")
            strasse = request.form.get("strasse")
            plz = request.form.get("plz")
            beschreibung = request.form.get("beschreibung")
            password = request.form.get("password")
            openTime = request.form.get("openTime")
    else:
        # should never be called
        return redirect(url_for("index"))


if __name__ == "__main__":
    # Create all tables within the application context
    with app.app_context():
        db.create_all()
        print(Kunde.query.all())
        print(Resto.query.all())

    print("Database tables created!")
    app.run(debug=True)
