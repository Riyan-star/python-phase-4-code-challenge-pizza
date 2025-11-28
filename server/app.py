from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------
# MODELS
# ----------------------

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship(
        'RestaurantPizza',
        back_populates='restaurant',
        cascade='all, delete-orphan'
    )

    def to_dict(self, only=None, include=None):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if only:
            result = {k: result[k] for k in only}
        if include and 'restaurant_pizzas' in include:
            result['restaurant_pizzas'] = [rp.to_dict(include=include.get('restaurant_pizzas', {})) for rp in self.restaurant_pizzas]
        return result

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship(
        'RestaurantPizza',
        back_populates='pizza',
        cascade='all, delete-orphan'
    )

    def to_dict(self, only=None, include=None):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if only:
            result = {k: result[k] for k in only}
        return result

class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value

    def to_dict(self, include=None):
        result = {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id
        }
        if include and 'pizza' in include:
            result['pizza'] = self.pizza.to_dict()
        if include and 'restaurant' in include:
            result['restaurant'] = self.restaurant.to_dict(only=('id','name','address'))
        return result

# ----------------------
# ROUTES
# ----------------------

# GET /restaurants
@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=('id','name','address')) for r in restaurants])

# GET /restaurants/<id>
@app.route('/restaurants/<int:id>')
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(
            only=('id','name','address'),
            include={'restaurant_pizzas': {'include': {'pizza': {}}}}
        ))
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# DELETE /restaurants/<id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# GET /pizzas
@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict() for p in pizzas])

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.to_dict(include={'pizza':{}, 'restaurant':{}})), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
    except Exception as e:
        return jsonify({"errors": ["Invalid data provided"]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
