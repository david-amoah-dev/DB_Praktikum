from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project2.db"
app.config['STATIC_FOLDER'] = 'static'
app.secret_key = 'supersecretkey'  # This is just an example, do not use simple keys like this in production

# initialize the app with the extension
db.init_app(app)


class Resto(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), unique = True, nullable = False)
    strasse = db.Column(db.String(20), unique = True, nullable = False)
    plz = db.Column(db.Integer(), unique = False, nullable = False)
    beschreibung = db.Column(db.String(555), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    openTime = db.Column(db.String(), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=200)

    def __repr__(self):
       return f"Resto('{self.name}')"

class Kunde(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    vorname = db.Column(db.String(20), unique = False, nullable = False)
    nachname = db.Column(db.String(20), unique = False, nullable = False)
    adresse = db.Column(db.String(20), unique = False, nullable = False)
    postleitzahl = db.Column(db.Integer(), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=200)


    def __repr__(self):
       return f"Kunde('{self.nachname}')"
    
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
    

with app.app_context():
  db.create_all()

@app.route('/registeringPage', methods=["GET"])
def registeringPage():
    return render_template("register.html")


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
    return render_template("restaurants.html")

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
    return render_template("restaurants.html")



@app.route('/', methods =["GET", "POST"])
def homepage():
    return redirect(url_for('login'))


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method== "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Received username: {username}, password: {password}") #debugging
    
        kunde = Kunde.query.filter_by(nachname=username).first()

        if kunde and kunde.password == password:
            print("password is right")#debugging
            session['username'] = kunde.nachname
            session['plz'] = kunde.postleitzahl
            session['id'] = kunde.id

            return redirect(url_for('CatchResto'))#showa the restaurants if any available
        else:
            return render_template('loginsaghar.html')
    
    
    return render_template('loginsaghar.html')

@app.route('/bestellansicht', methods =["GET", "POST"])
def bestellansicht():

    orders = Orders.query.order_by(
        # numbers to group orders by priority, time.desc() to sort by decending time after being grouped by their status
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2},value=Orders.lieferstatus),Orders.time.desc()).all()
    return render_template('resto_Bestellansicht.html', orders = orders)
    
@app.route('/restaurants', methods=["GET"])
def CatchResto():
    #catch the PLZ from session(for now the static version)
    kunde_postleitzahl = session.get('plz')

    #catch the restaurant with the same PLZ
    restaurants= Resto.query.filter_by(plz=kunde_postleitzahl).all()
    return render_template('restaurants.html', restaurants = restaurants)


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


@app.route('/add_order', methods=["POST"])
def add_order():
    if request.method == "POST": 
        if "user" in session:
            user = session["user"]
            if user["type"] == "Kunde":
            # Fetch the Kunde user from the database using the stored ID
                kunde = Kunde.query.get_or_404(user["id"])
                
        name = {kunde.nachname, kunde.vorname}
        adresse = kunde.adresse
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
    
if __name__ == '__main__':
    app.run(debug=True)