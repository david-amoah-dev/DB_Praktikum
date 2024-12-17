from flask import Flask, redirect, render_template, request, url_for
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
    wallet = db.Column(db.Integer, nullable=False, default=0)

class Kunde(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    vorname = db.Column(db.String(20), unique = False, nullable = False)
    nachname = db.Column(db.String(20), unique = False, nullable = False)
    adresse = db.Column(db.String(20), unique = False, nullable = False)
    postleitzahl = db.Column(db.Integer(), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=100)

@app.route('/', methods =["GET", "POST"])
def homepage():
    return render_template('index.html')
# pop up request
@app.route('/registerKunde', methods=["POST"])
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
    return render_template("dog.html")

@app.route('/registerResto', methods=["POST"])
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
    return render_template("index.html")


if __name__ == "__main__":
    # Create all tables within the application context
    with app.app_context():
        db.create_all()
        print(Kunde.query.all())
        print(Resto.query.all())

    print("Database tables created!")
    app.run(debug=True)
