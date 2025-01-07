from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone

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

class Orders(db.Model):
    # Zeit ohne Millisekunden
    time = db.Column(DateTime, default=lambda: datetime.now().replace(microsecond=0))
    id = db.Column(db.Integer, primary_key=True)
    lieferstatus = db.Column(db.String(50), nullable=False, default = "in Bearbeitung")
    items = db.Column(db.Text, nullable=False)  
    preis = db.Column(db.Float, nullable=False)  
    menge = db.Column(db.Integer, nullable=False) 
    zahlungsstatus = db.Column(db.String(50), nullable=False, default = "ausstehend")
    liefergebuehren = db.Column(db.Float, nullable=False)
    gesamt = db.Column(db.Float, nullable=False)
    anmerkungen = db.Column(db.Text, nullable=True)

@app.route('/', methods =["GET", "POST"])
def bestellansicht():

    orders = Orders.query.order_by(
        # numbers to group orders by priority, time.desc() to sort by decending time after being grouped by their status
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2},value=Orders.lieferstatus),Orders.time.desc()).all()
    return render_template('resto_Bestellansicht.html', orders=orders)
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


@app.route('/add_order', methods=["POST"])
def add_order():
    if request.method == "POST":
        lieferstatus = request.form.get("lieferstatus")
        items = request.form.get("items")

        # preis ist nicht static gespeichert!!
        preis = float(request.form.get("preis"))

        menge = int(request.form.get("menge"))
        zahlungsstatus = request.form.get("zahlungsstatus")
        liefergebuehren = float(request.form.get("liefergebuehren"))
        anmerkungen = request.form.get("anmerkungen")

        # muss noch angepasst werden
        gesamt = preis * menge + liefergebuehren

        new_order = Orders(
            lieferstatus=lieferstatus,
            items=items,
            preis=preis,
            menge=menge,
            zahlungsstatus=zahlungsstatus,
            liefergebuehren=liefergebuehren,
            gesamt=gesamt,
            anmerkungen = anmerkungen
        )

        db.session.add(new_order)
        db.session.commit()

        return redirect(url_for('bestellansicht'))

 # edit redirecting!!
@app.route('/order/<int:order_id>/decline', methods=['POST'])
def decline_order(order_id):
    order = Orders.query.get_or_404(order_id)
    order.lieferstatus = "storniert" 
    order.zahlungsstatus = "abgebrochen"
    db.session.commit()
    return redirect(url_for('bestellansicht'))
@app.route('/order/<int:order_id>/accept', methods=['POST'])
def accept_order(order_id):
    order = Orders.query.get_or_404(order_id)
    order.lieferstatus = "in Zubereitung" 
    order.zahlungsstatus = "abgeschlossen"
    db.session.commit()
    return redirect(url_for('bestellansicht'))
@app.route('/order/<int:order_id>/finished', methods=['POST'])
def finished_order(order_id):
    order = Orders.query.get_or_404(order_id)
    order.lieferstatus = "abgeschlossen" 
    db.session.commit()
    return redirect(url_for('bestellansicht'))

if __name__ == "__main__":
    # Create all tables within the application context
    with app.app_context():
        db.create_all()

    app.run(debug=True)


## Items von David und login, bestellung von Simon