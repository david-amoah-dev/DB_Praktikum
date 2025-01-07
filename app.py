import sqlite3
from flask import Flask, url_for, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

#create the app-------------------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
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

class Kunde(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    vorname = db.Column(db.String(20), unique = False, nullable = False)
    nachname = db.Column(db.String(20), unique = False, nullable = False)
    adresse = db.Column(db.String(20), unique = False, nullable = False)
    postleitzahl = db.Column(db.Integer(), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    wallet = db.Column(db.Integer, nullable=False, default=100)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    itmname = db.Column(db.String(20), unique = False, nullable = True)
    description = db.Column(db.String(20), unique = False, nullable = True)
    price = db.Column(db.Integer(), nullable = True)
    # bild = db.Column()
    category = db.Column(db.String(), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    ordrtitle = db.Column(db.String(20), unique = False, nullable = False)
    # status = db.Column()
    # item = db.Column()
    # customer = db.Column()
    # datetime = db.Column()
    comment = db.Column(db.String(200), unique = False, nullable = False)
    # ammountOfItem = db.Column(db.Integer(), nullable = False)

# Page routes----------------------------------------------------------------------------------
@app.route("/")
def homepage():
     return render_template('Welcomepage.html')

# Customer Pages----------------------------------------------
@app.route("/cstmlogin")
def cstmlogin():
    return render_template('CustomerView-Login.html')

@app.route("/cstmprofile")
def cstmprofile():
    return render_template('CustomerView-Profile.html')

@app.route("/cstmwaren")
def cstmwaren():
    return render_template('CustomerView-Warenkorb.html')

@app.route("/cstmhome")
def cstmpage():
    return render_template('CustomerView-RestaurantOverview.html')

@app.route("/cstmbsth")
def cstmbsth():
    return render_template('CustomerView-Bestellhistorie.html')

@app.route("/cstmrstdtl")
def cstmrstdtl():
    return render_template('CustomerView-RestaurantDetails.html')


# Restaurant Pages-------------------------------------------------
@app.route("/rstrlogin")
def rstrlogin():
    return render_template('RestaurantView-Login.html')

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
        ordrtitle = request.form.get("upitemname")
        comment = request.form.get("updescription")

        # update Item
        item = Item(itmname = upitemname,description = updescription,price = upprice,category = upcategory)
        print(f"Received: {upitmname}, {updescription}, {upprice}, {upcategory}")
        db.session.update(item)
        db.session.commit()
    return redirect(url_for("rstrspkt"))

@app.route("/itmadd", methods = ['POST'])
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

#-----------------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # print(Kunde.query.all(()))
        # print(Resto.query.all(()))
        print(Item.query.all())
        # print(Order.query.all())
    app.run(port=5000, debug=True, threaded=True)

# Session implementieren
# nicht vergessen logout zu implementieren    # with app.app_context():

# login pw überprüfen
# def check(username, password):
