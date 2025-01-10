from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

#   $ python -m flask --app [Dateiname] run

app.secret_key = "well well well fuckas"

@app.route("/")
def index():
    if not "user" in session:
        return render_template("index.html")
    user = session["user"]
    return render_template("index.html", username = user)

@app.route("/profile/")
def profile():
    if not "user" in session:
        return redirect(url_for("login"))
    user = session["user"]
    return render_template("profile.html", content=[user+".name", user+".address"])
    # replace "content" with database results
    
    
@app.route("/profile/update/", methods=["POST", "GET"])
def profile_update():
    if not "user" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("profile_update.html")
    elif request.method == "POST":
        new_username = request.form["new_username"]
        session["user"] = new_username
        # insert user in database
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




if __name__ == "__main__":
    # Create all tables within the application context
    with app.app_context():
        db.create_all()
        

    print("Database tables created!")
    app.run(debug=True)
