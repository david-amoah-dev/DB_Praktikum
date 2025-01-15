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
    anmerkungen = db.Column(db.Text, nullable = True)
    postleitzahl = db.Column(db.Text, nullable=False)

############## item Tabelle mit restaurantid
class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    itmname = db.Column(db.String(20), unique = False, nullable = True)
    description = db.Column(db.String(20), unique = False, nullable = True)
    price = db.Column(db.Integer(), nullable = True)
    # bild = db.Column()
    category = db.Column(db.String(), nullable=True)
    restoid = db.Column(db.Integer, nullable=False)
###############

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
            return redirect(url_for('CatchResto'))#showa the restaurants if any available
        elif resto and resto.password == password:
            user = {"id" : resto.id, "type" : "Resto", "plz" : resto.plz, "username" : resto.name}
            session["user"] = user

            return redirect(url_for('rstrspkt', restaurant_id = resto.id))
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

    return render_template('kunde_Bestellansicht.html', orders=orders, json=json)



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

    return render_template('resto_Bestellansicht.html', orders=orders, json=json)

    
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

# delete this
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

    
@app.route("/summary/")
def summary():
    # to do change to get items from session
    #item1 = {"name" : "Name1", "description" : "Text1", "price" : 1.20, "amount" : 5, "restoID" : 1}
    #item2 = {"name" : "Name2", "description" : "Text2", "price" : 2.20, "amount" : 4, "restoID" : 1}
    #item3 = {"name" : "Name3", "description" : "Text3", "price" : 3.20, "amount" : 3, "restoID" : 1}
    #items = [item1, item2, item3]
    #session["items"] = items

    if not "user" in session:
        return redirect(url_for("login"))
    if not "items" in session:
        return redirect(url_for("login"))
    items_dict = session["items"]

    

    
    
    #session["items"] = items_dict 

    # calculate price 
    total = 0.0
    for elem in items_dict:
        total += float(elem["price"]) * int(elem["amount"])
        
    final = f"{total:.2f}"

    return render_template("summary.html", content = items_dict, total = final)

@app.route("/new_order/", methods=["POST"])
def new_order():
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
        total += float(elem["price"]) * int(elem["amount"])
    finalprice = f"{total:.2f}"

    # serialize Items
    serializedItems = json.dumps(items) 

    if user.wallet - total<0:
        new_order = Orders(
        lieferstatus = "storniert",
        items = serializedItems,
        preis = float(finalprice),
        zahlungsstatus = "abgebrochen",
        name = f"{user.vorname} {user.nachname}",
        adresse = user.adresse,
        kunde_id = userID,
        resto_id = restoID,
        anmerkungen = "Geld unzureichend",
        postleitzahl = user.postleitzahl
    )
    else:
        new_order = Orders(
            lieferstatus = "in Bearbeitung",
            items = serializedItems,
            preis = float(finalprice),
            zahlungsstatus = "ausstehend",
            name = f"{user.vorname} {user.nachname}",
            adresse = user.adresse,
            kunde_id = userID,
            resto_id = restoID,
            anmerkungen = request.form.get("anmerkungen"),
            postleitzahl = user.postleitzahl
        )
    db.session.add(new_order)
    db.session.commit()
    
    return redirect(url_for("bestellansichtKunde"))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear all session data
    session.clear()  # This clears the entire session
    return redirect(url_for('login'))  # Redirect to login page after logout


#was man braucht um richtige restaurant seite hochzuladen(nur test)
@app.route('/test/<int:restaurant_id>', methods=['GET', 'POST'])
def test( restaurant_id):
    restaurant = Resto.query.get_or_404(restaurant_id)

    return render_template("test.html", restaurant=restaurant)

#############################################
#ansicht der details zu dem ausgewählten restaurant (also die Speisekarte)
@app.route("/cstmrstdtl/<int:restaurant_id>", methods=['GET', 'POST'])
def cstmrstdtl(restaurant_id):
    items = db.session.execute(db.select(Item).filter_by(restoid = restaurant_id)).scalars()
    restaurant = Resto.query.get_or_404(restaurant_id)
    return render_template('CustomerView-RestaurantDetails.html', items=items, restaurant=restaurant)

#ansicht des eingeloggten restaurants zum bearbeiten der eigenen Restaurant Speisekarte
@app.route("/rstrspkt/<int:restaurant_id>", methods=['GET', 'POST'])
def rstrspkt(restaurant_id):
    items = db.session.execute(db.select(Item).filter_by(restoid = restaurant_id)).scalars()
    restaurant = Resto.query.get_or_404(restaurant_id)
    return render_template('RestaurantView-Speisekarte.html', items=items, restaurant=restaurant)

# Item hinzufügen zu der Speisekarte des jeweiligen restaurants
@app.route("/itmadd/<int:restaurant_id>", methods = ['GET','POST'])
def itmadd(restaurant_id):
    restaurant = Resto.query.get_or_404(restaurant_id)
    if request.method == "POST":
        itmname = request.form.get("itemname")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        # create Item
        new_item = Item(itmname = itmname,description = description,price = price,category = category, restoid = restaurant_id)
        print(f"Received: {itmname}, {description}, {price}, {category}")
        db.session.add(new_item)
        db.session.commit()
    return redirect(url_for("rstrspkt", restaurant_id = restaurant_id))

# löschen eines items aus der Speisekarte
@app.route("/delitm/<int:mid>", methods = ['GET','POST'])
def delitm(mid):
    item = db.session.execute(db.select(Item).filter_by(id = mid)).scalar_one()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("rstrspkt", restaurant_id = item.restoid))

# ändern eines items aus der Speisekarte
@app.route("/upditm/<int:updid>", methods = ['GET','POST'])
def upditm(updid):
    item = db.session.execute(db.select(Item).filter_by(id = updid)).scalar_one()
    if request.method == "POST":
        upitmname = request.form.get("upitemname")
        updescription = request.form.get("updescription")
        upprice = request.form.get("upprice")
        upcategory = request.form.get("upcategory")

        # update Item

        updated_item = Item.query.get_or_404(updid)

        updated_item.itmname = upitmname
        updated_item.description = updescription
        updated_item.price = upprice
        updated_item.category = upcategory

        print(f"Received: {upitmname}, {updescription}, {upprice}, {upcategory}")
        #db.session.update(item)
        db.session.commit()
    return redirect(url_for("rstrspkt", restaurant_id= item.restoid))

# Hochladen von Bildern (an diesem teil muss noch gearbeitet werden)
@app.route("/upload/", methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['']
        f.save('/static/images/')
###############################################

@app.route("/check_new_orders")
def check_new_orders():
    if 'user' not in session or session['user']['type'] != 'Resto':
        return {"new_order": False, "latest_order_id": None}
    
    resto_id = session['user']['id']
    latest_order = Orders.query.filter_by(resto_id=resto_id).order_by(Orders.time.desc()).first()
    # new_order = Orders(
    #     lieferstatus="in Bearbeitung",
    #     items='[{"name": "Pizza", "price": 12, "amount": 1}]',
    #     preis=12.0,
    #     zahlungsstatus="ausstehend",
    #     name="John Doe",
    #     adresse="123 Street",
    #     kunde_id=1,
    #     resto_id=1,
    #     postleitzahl="12345")

    # db.session.add(new_order)
    # db.session.commit()
    if latest_order and latest_order.lieferstatus == "in Bearbeitung":
        return {"new_order": True, "latest_order_id": latest_order.id}

    return {"new_order": False, "latest_order_id": None}

@app.route("/submit_cart", methods=["POST"])
def submit_cart():
    # Get the JSON data from the request
    cart_data = request.get_json()
    
    # format data to dicts in array
    items_dict = []
    for elem in cart_data:
        temp = {
            "name" : elem[0],
            "description" : elem[1],
            "price" : float(elem[2]),
            "amount" : elem[3],
            "restoID" : elem[4]
        }
        items_dict += [temp]
    session["items"] = items_dict
    return redirect(url_for("summary"))



if __name__ == '__main__':
    app.run(debug=True)




# redirect nach login kunde
# item price type float
# logout func
# delete profile_alternative.html