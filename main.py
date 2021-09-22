from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# Get a random cafe
@app.route("/random", methods=["GET"])
def random_cafe():
    all_cafes = db.session.query(Cafe).all()
    cafe = random.choice(all_cafes)
    return jsonify(cafe.to_dict())


# Get all
@app.route('/all', methods=["GET"])
def get_all():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


# Get all in a given location
@app.route('/search')
def search_location():
    # Picks a query out of the url
    query_location = request.args.get("location")
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# Add a cafe
@app.route('/add', methods=["POST"])
def add_cafe():
    print(request.form["name"])
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        seats=request.form["seats"],
        has_toilet=bool(request.form["has_toilet"]),
        has_wifi=bool(request.form["has_wifi"]),
        has_sockets=bool(request.form["has_sockets"]),
        can_take_calls=bool(request.form["can_take_calls"]),
        coffee_price=request.form["coffee_price"],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return "Cafe successfully added."


# HTTP PUT/PATCH - Update a Cafe
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    query_price = request.args.get("new_price")
    if query_price:
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            cafe.coffee_price = query_price
            db.session.commit()
            # Just add the code after the jsonify method. 200 = Ok
            return jsonify(response={"success": "Successfully updated the price."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete a Cafe
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    auth_token = request.args.get("token")
    if auth_token == "Hey_now!":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Ima need a valid token from you."}), 403


if __name__ == '__main__':
    app.run(debug=True)
