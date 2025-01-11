from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
import json

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project2.db"
app.config['STATIC_FOLDER'] = 'static'
app.secret_key = 'someKey'  # This is just an example, do not use simple keys like this in production

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
    zahlungsstatus = db.Column(db.String(50), nullable=False, default = "ausstehend")
    name = db.Column(db.Text, nullable=False) 
    adresse = db.Column(db.Text, nullable=False) 
    kunde_id = db.Column(db.Integer, nullable=False)
    resto_id = db.Column(db.Integer, nullable=False)
    ## anmerkungen = db.Column(db.Text, nullable = True)


with app.app_context():
  db.create_all()

@app.route('/', methods =["GET", "POST"])
def homepage():
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))



@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method== "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Received username: {username}, password: {password}") #debugging
    
        kunde = Kunde.query.filter_by(nachname=username).first()
        resto = Resto.query.filter_by(name=username).first()


        if kunde and kunde.password == password:
            print("password is right")#debugging
            session['user'] = {
                'id': kunde.id,
                'type': 'Kunde',
                'plz': kunde.postleitzahl,
                'username': kunde.nachname
            }
            return redirect(url_for('bestellansichtKunde'))#showa the restaurants if any available
        elif resto and resto.password == password:
            user = {"id" : resto.id, "type" : "Resto", "plz" : resto.plz, "username" : resto.name}
            session["user"] = user

            return render_template('resgistersaghar.html', name=resto.name)
    else :
        return render_template('loginsaghar.html')
        
    
  

@app.route('/bestellansichtKunde', methods =["GET", "POST"])
def bestellansichtKunde():

    if 'user' not in session or session['user']['type'] != 'Kunde':
        return redirect(url_for('login'))

    kunde_id = session['user']['id']

    # Query orders specific to the logged-in customer, ordered by priority and time
    orders = Orders.query.filter_by(kunde_id=kunde_id).order_by(
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2}, 
                value=Orders.lieferstatus),
        Orders.time.desc()
    ).all()
    
    return render_template('kunde_Bestellansicht.html', orders=orders)



@app.route('/bestellansichtResto', methods =["GET", "POST"])
def bestellansichtResto():
    if 'user' not in session or session['user']['type'] != 'Resto':
        return redirect(url_for('login'))

    resto_id = session['user']['id']

    # Query orders specific to the logged-in customer, ordered by priority and time
    orders = Orders.query.filter_by(resto_id=resto_id).order_by(
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2}, 
                value=Orders.lieferstatus),
        Orders.time.desc()
    ).all()
    
    return render_template('resto_Bestellansicht.html', orders=orders)
    orders = Orders.query.order_by(
        # numbers to group orders by priority, time.desc() to sort by decending time after being grouped by their status
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2},value=Orders.lieferstatus),Orders.time.desc()).all()
    return render_template('resto_Bestellansicht.html', orders = orders)
    
@app.route('/restaurants', methods=["GET"])
def CatchResto():
    #catch the PLZ from session(for now the static version)
    kunde_postleitzahl = session['user'].get('plz')

    #catch the restaurant with the same PLZ
    restaurants= Resto.query.filter_by(plz=kunde_postleitzahl).all()
    return render_template('restaurants.html', restaurants = restaurants)


@app.route('/Menu', methods=["GET"])
def OpenRestaurant(restaurant_id):

    restaurant = Resto.query.get_or_404(restaurant_id)

    return render_template('RestaurantView-Speisekarte.html', restaurant=restaurant)



@app.route("/profile/")
def profile():
    if not session.get("user"):
        return redirect(url_for("login"))
    user1 = session["user"]

    if user1["type"] == "Kunde":
        user = Kunde.query.get_or_404(user1["id"])
    else:
        user = Resto.query.get_or_404(user1["id"])
    return render_template("profile.html", content=user, userType = user1["type"])
    
@app.route("/profile/update/", methods=["POST", "GET"])
def profile_update():
    user = session["user"]
    if user["type"] == "Kunde":
        if request.method == "POST":

            vorname = request.form.get("vorname")
            nachname = request.form.get("nachname")
            adresse = request.form.get("adresse")
            postleitzahl = request.form.get("postleitzahl")
            password = request.form.get("password")

            user = Kunde.query.get_or_404(user["id"])

            user.vorname = vorname
            user.nachname = nachname
            user.adresse = adresse
            user.postleitzahl = postleitzahl
            user.password = password

            db.session.commit()
    else: 
        if request.method == "POST":

            name = request.form.get("name")
            strasse = request.form.get("strasse")
            plz = request.form.get("plz")
            beschreibung = request.form.get("beschreibung")
            password = request.form.get("password")
            openTime = request.form.get("openTime")

            user = Resto.query.get_or_404(user["id"])
            
            user.name = name
            user.strasse = strasse
            user.plz = plz
            user.beschreibung = beschreibung
            user.password = password
            user.openTime = openTime

            db.session.commit()
    
    return redirect(url_for("profile"))



 # edit redirecting!! für kunde und resto bearbeiten
@app.route('/order/<int:order_id>/decline', methods=['POST'])
def decline_order(order_id):
    order = Orders.query.get_or_404(order_id)
    order.lieferstatus = "storniert" 
    order.zahlungsstatus = "abgebrochen"
    db.session.commit()
    return redirect(request.referrer)
@app.route('/order/<int:order_id>/accept', methods=['POST'])
def accept_order(order_id):
    order = Orders.query.get_or_404(order_id)
    user = Kunde.query.get_or_404(order.kunde_id)
    resto = Resto.query.get_or_404(order.resto_id)

    #update User Wallet
    userWallet = float(user.wallet)
    userWallet -= float(order.preis)
    finalUserWallet = f"{userWallet:.2f}"
    user.wallet = finalUserWallet

    #update Resto Wallet
    restoWallet = float(resto.wallet)
    restoWallet += (float(order.preis) * 0.85) # remove cut for lfrsptz
    finalRestoWallet = f"{restoWallet:.2f}"
    resto.wallet = finalRestoWallet

    # update order status
    order.lieferstatus = "in Zubereitung" 
    order.zahlungsstatus = "abgeschlossen"
    db.session.commit()
    return redirect(request.referrer)
@app.route('/order/<int:order_id>/finished', methods=['POST'])
def finished_order(order_id):
    order = Orders.query.get_or_404(order_id)
    order.lieferstatus = "abgeschlossen" 
    db.session.commit()
    return redirect(request.referrer)


@app.route('/add_order', methods=["POST"])
def add_order():
    name = "unknown"
    adresse = "unknown"
    if request.method == "POST": 
        if 'user' in session:  # Überprüfen, ob der Benutzer eingeloggt ist
            user = session['user']
            kunde = Kunde.query.get_or_404( user['id'])  # Hole den Kunden mit der ID aus der Session
            name = f"{kunde.vorname} {kunde.nachname}"  # Setze den vollständigen Namen (Vorname + Nachname)
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
            anmerkungen = anmerkungen,
            name=name,
            adresse= adresse
        )
        db.session.add(new_order)
        db.session.commit()

        return redirect(url_for('bestellansichtKunde'))
    #muss auch eine für resto geschrieen werden
    
@app.route("/summary/")
def summary():
    # to do change to get items from session
    item1 = {"name" : "Name1", "description" : "Text1", "price" : 1.20, "amount" : 5, "restoID" : 1}
    item2 = {"name" : "Name2", "description" : "Text2", "price" : 2.20, "amount" : 4, "restoID" : 1}
    item3 = {"name" : "Name3", "description" : "Text3", "price" : 3.20, "amount" : 3, "restoID" : 1}
    items = [item1, item2, item3]
    session["items"] = items

    if not "user" in session:
        return redirect(url_for("login"))
#   if not "items" in session:
#       return redirect(url_for("index"))
#   items = session["items"]

    # calculate price 
    total = 0.0
    for elem in items:
        total += elem["price"] * elem["amount"]
    final = f"{total:.2f}"

    return render_template("summary.html", content = items, total = final)

@app.route("/new_order/")
def order():
    if not "user" in session:
        return redirect(url_for("login"))
    if not "items" in session:
        return redirect(url_for("login"))
    # get session elements
    userID = session["user"]["id"]
    items = session["items"]
    restoID = items[0]["restoID"]

    user = Kunde.query.get_or_404(userID)

    # calculate price
    total = 0.0
    for elem in items:
        total += elem["price"] * elem["amount"]
    finalprice = f"{total:.2f}"

    # serialize Items
    serializedItems = json.dumps(items) 

    new_order = Orders(
        lieferstatus = "in Bearbeitung",
        items = serializedItems,
        preis = float(finalprice),
        zahlungsstatus = "ausstehend",
        name = f"{user.vorname} {user.nachname}",
        adresse = user.adresse,
        kunde_id = userID,
        resto_id = restoID,
        ## Anmerkungen fehlen
    )
    db.session.add(new_order)
    db.session.commit()
    
    return redirect(url_for("bestellansichtKunde"))

@app.route('/logout', methods=['POST'])
def logout():
    # Clear all session data
    session.clear()  # This clears the entire session
    return redirect(url_for('login'))  # Redirect to login page after logout


#was man braucht um richtige restaurant seite hochzuladen(nur test)
@app.route('/test/<int:restaurant_id>', methods=['GET', 'POST'])
def test( restaurant_id):
    restaurant = Resto.query.get_or_404(restaurant_id)

    return render_template("test.html", restaurant=restaurant)

    
if __name__ == '__main__':
    app.run(debug=True)




# Item Ansicht in Bestellansicht updaten -> veränderte Tabellenstruktur Orders
# Input session["Items"]
# Bestellanischt Buttons annehmen/ablehnen not working as intended?
# funktion add_order noch benötigt? was ist mit brauch man auch für resto gemeint?