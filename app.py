import sqlite3
from flask import Flask, url_for, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

#create the app-------------------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project3.db"
db.init_app(app)

app.secret_key = "idk just some secret key i guess"

#db Models bzw Tables-------------------------------------------------------------------------------
class Resto(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), unique = False, nullable = False)
    strasse = db.Column(db.String(20), unique = True, nullable = False)
    plz = db.Column(db.Integer(), unique = False, nullable = False)
    beschreibung = db.Column(db.String(555), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    openTime = db.Column(db.String(), nullable = False)
    # lradius = db.Column(db.Integer(), unique = False, nullable = False)
    # bild = db.Column()
    wallet = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
       return f"Resto('{self.name}')"

class Kunde(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    vorname = db.Column(db.String(20), unique = False, nullable = False)
    nachname = db.Column(db.String(20), unique = False, nullable = False)
    adresse = db.Column(db.String(20), unique = False, nullable = False)
    postleitzahl = db.Column(db.Integer(), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=100)

    def __repr__(self):
       return f"Kunde('{self.nachname}')"

class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    itmname = db.Column(db.String(20), unique = False, nullable = True)
    description = db.Column(db.String(20), unique = False, nullable = True)
    price = db.Column(db.Integer(), nullable = True)
    # bild = db.Column()
    category = db.Column(db.String(), nullable=True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    ordrtitle = db.Column(db.String(20), unique = False, nullable = True)
    time = db.Column(DateTime, default=lambda:datetime.now().replace(microsecond=0))
    lieferstatus = db.Column(db.String(50), nullable=False, default = "in Bearbeitung")
    items = db.Column(db.Text, nullable=False)
    preis = db.Column(db.Float, nullable=False)
    menge = db.Column(db.Integer, nullable=False)
    zahlungsstatus = db.Column(db.String(50), nullable=False, default = "ausstehend")
    liefergebuehren = db.Column(db.Float, nullable=True)
    gesamt = db.Column(db.Float, nullable=False)
    anmerkungen = db.Column(db.String(200), unique = False, nullable = True)
    # ammountOfItem = db.Column(db.Integer(), nullable = False)
    # customer = db.Column()

# Page routes----------------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def homepage():
     return render_template('Welcomepage.html')

# Customer Pages----------------------------------------------
@app.route("/cstmprofile")
def cstmprofile():
    return render_template('CustomerView-Profile.html')

@app.route("/cstmwaren")
def cstmwaren():
    return render_template('CustomerView-Warenkorb.html')

@app.route("/cstmhome")
def cstmpage():
    #catch the PLZ from session(for now the static version)
    kunde_postleitzahl = session.get('plz')

    #catch the restaurant with the same PLZ
    restaurants= Resto.query.filter_by(plz=kunde_postleitzahl).all()
    return render_template('CustomerView-RestaurantOverview.html', restaurants = restaurants)


@app.route("/cstmbsth")
def cstmbsth():
    orders = Orders.query.order_by(
        # numbers to group orders by priority, time.desc() to sort by decending time after being grouped by their status
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2},value=Orders.lieferstatus),Orders.time.desc()).all()
    return render_template('CustomerView-Bestellhistorie.html', orders = orders)

@app.route("/cstmrstdtl")
def cstmrstdtl():
    items = db.session.execute(db.select(Item)).scalars()
    return render_template('CustomerView-RestaurantDetails.html', items=items)


# Restaurant Pages-------------------------------------------------
@app.route("/rstrbstlh")
def rstrbstlh():
    return render_template('RestaurantView-Bestellhistorie.html')

@app.route("/rstrprofile")
def rstrprofile():
    return render_template('RestaurantView-Profile.html')

@app.route("/rstrspkt")
def rstrspkt():
    items = db.session.execute(db.select(Item)).scalars()
    return render_template('RestaurantView-Speisekarte.html', items=items)

@app.route("/items")
def item_list():
    items = db.session.execute(db.select(Item)).scalars()
    return render_template('itemlist.html', items=items)

## functional app routes------------------------------------------
@app.route("/itmadd", methods = ['POST'])
def itmadd():
    if request.method == "POST":
        itmname = request.form.get("itemname")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        # create Item
        new_item = Item(itmname = itmname,description = description,price = price,category = category)
        print(f"Received: {itmname}, {description}, {price}, {category}")
        db.session.add(new_item)
        db.session.commit()
    return redirect(url_for("rstrspkt"))

@app.route("/delitm/<int:mid>", methods = ['GET','POST'])
def delitm(mid):
    item = db.session.execute(db.select(Item).filter_by(id = mid)).scalar_one()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("rstrspkt"))

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
    return redirect(url_for("rstrspkt"))

@app.route("/ordradd", methods = ['POST']) #needs some work
def ordradd():
    if request.method == "POST":
        itmname = request.form.get("itemname")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        # create Item
        new_order = Item(itmname = itmname,description = description,price = price,category = category)
        print(f"Received: {itmname}, {description}, {price}, {category}")
        db.session.add(new_order)
        db.session.commit()
    return redirect(url_for("rstrspkt"))

#___________________________________________Dinhs routes___________________________________
@app.route('/bestellansicht', methods =["GET", "POST"])
def bestellansicht():

    orders = Orders.query.order_by(
        # numbers to group orders by priority, time.desc() to sort by decending time after being grouped by their status
        db.case({"in Bearbeitung": 1, "in Zubereitung": 1, "abgeschlossen": 2, "storniert": 2},value=Orders.lieferstatus),Orders.time.desc()).all()
    return render_template('RestaurantView-Bestellhistorie.html', orders = orders)

#________________________________________

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

# ____________________________________________

@app.route('/add_order', methods=["POST"])
def add_order():
    if request.method == "POST":
        #if "user" in session:
         #   user = session["user"]
          #  if user["type"] == "Kunde":
            # Fetch the Kunde user from the database using the stored ID
        #        kunde = Kunde.query.get_or_404(user["id"])

        #name = {kunde.nachname, kunde.vorname}
        #adresse = kunde.adresse
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

# __________________________________________saghars routes___________________________________

# __________________________register Method_________________
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
    return render_template("Welcomepage.html")

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
    return render_template("Welcomepage.html")

# ______________________login Method________________
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
            session['username'] = kunde.nachname
            session['plz'] = kunde.postleitzahl
            session['id'] = kunde.id

            return redirect(url_for('cstmpage'))#showa the restaurants if any available
        elif resto and resto.password == password:
            session['username']= resto.name
            session['plz'] = resto.plz
            session['id'] = resto.id

            return redirect(url_for('rstrspkt'))


    return render_template('Welcomepage.html')

# ____________________________________________simons routes____________________________________________
@app.route("/home")
def index():
    if not session.get("username"):
        return render_template("Welcomepage.html")
    user = session["username"]
    return redirect(url_for("cstmpage"))
        # Homepage Restaurantübersicht

# todo delete this
@app.route("/homepage/")
def homepagesim():
    if not "user" in session:
        return render_template("Welcomepage.html")
    user = session["user"]
    return render_template("Welcomepage.html", username = user)

# ______________________reigister / logins________________
# pop up request

# delete this
#@app.route("/login/", methods=["POST", "GET"])
#def login():
#    if "user" in session:
#        return redirect(url_for("cstmprofile"))
#    if request.method == "GET":
#        return render_template("Welcomepage.html")
#    elif request.method == "POST":
#        temp = request.form["username"]
#        user1 = {"id" : 1, "type" : "Kunde"}
#        session["user"] = user1
#        return redirect(url_for("profile"))
#    else:
#        return redirect(url_for("index"))
        # error message?

@app.route("/logout/") # logout is complete
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

# ________________profile____________
@app.route("/profile/") #important to look at # should work now
def profile():
    if not session.get("user"):
        return redirect(url_for("login"))
    user1 = session["user"]
    print(user1)
    user2 = None
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
# ________________________summary____________________________
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



#-----------------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # print(Kunde.query.all(()))
        # print(Resto.query.all(()))
        print(Item.query.all())
        # print(Order.query.all())
    app.run(port=5000, debug=True, threaded=True)

# Session implementieren!!!
# nicht vergessen logout zu implementieren    # with app.app_context():

# login pw überprüfen
# def check(username, password):

# session insert after account creation