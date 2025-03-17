#!/usr/bin/env python3  # Shebang line to specify the script should be run with Python 3

# Import required modules and packages
from models import db, Restaurant, RestaurantPizza, Pizza  # Import database and model classes
from flask_migrate import Migrate  # For handling database migrations
from flask import Flask, request, make_response, jsonify  # Flask core modules
from flask_restful import Api, Resource  # Flask-RESTful for creating REST APIs
import os  # For handling file paths and environment variables

# Determine the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get absolute path of current directory
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")  # Use environment DB_URI or default to local SQLite

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE  # Set database URI for SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable unnecessary feature
app.json.compact = False  # Format JSON output with better readability

# Set up migration and database initialization
migrate = Migrate(app, db)  # Initialize Flask-Migrate with app and db
db.init_app(app)  # Bind SQLAlchemy db to Flask app

# Initialize Flask-RESTful API
api = Api(app)

# Basic route to confirm server is running
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Resource for handling GET requests to /restaurants
class RestaurantsResource(Resource):
    def get(self):
        """GET /restaurants - Returns a list of all restaurants"""
        restaurants = Restaurant.query.all()  # Fetch all restaurant records
        return make_response(jsonify([restaurant.to_dict() for restaurant in restaurants]), 200)  # Serialize and return

# Resource for handling GET and DELETE for a specific restaurant
class RestaurantDetailResource(Resource):
    def get(self, id):
        """GET /restaurants/<id> - Returns a single restaurant and its pizzas"""
        restaurant = Restaurant.query.get(id)  # Fetch restaurant by ID
        if restaurant:
            # Serialize with optional rule to exclude redundant data
            return make_response(jsonify(restaurant.to_dict(rules=('-restaurant_pizzas.restaurant',))), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)  # Return error if not found

    def delete(self, id):
        """DELETE /restaurants/<id> - Deletes a restaurant and its associated restaurant_pizzas"""
        restaurant = Restaurant.query.get(id)  # Fetch restaurant by ID
        if restaurant:
            db.session.delete(restaurant)  # Delete from database
            db.session.commit()  # Commit transaction
            return make_response('', 204)  # Return no content status
        return make_response(jsonify({"error": "Restaurant not found"}), 404)  # Return error if not found

# Resource for handling GET requests to /pizzas
class PizzasResource(Resource):
    def get(self):
        """GET /pizzas - Returns a list of all pizzas"""
        pizzas = Pizza.query.all()  # Fetch all pizza records
        return make_response(jsonify([pizza.to_dict() for pizza in pizzas]), 200)  # Serialize and return

# Resource for handling POST requests to /restaurant_pizzas
class RestaurantPizzasResource(Resource):
    def post(self):
        """POST /restaurant_pizzas - Creates a new RestaurantPizza"""
        data = request.get_json()  # Parse JSON data from request body

        try:
            # Create new RestaurantPizza record with provided data
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"]
            )
            db.session.add(new_restaurant_pizza)  # Add to session
            db.session.commit()  # Commit to database

            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)  # Return created object with 201 status

        except ValueError:
            # Return validation error if any issue occurs during creation
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

# Register API resources with their corresponding endpoints
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantDetailResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")

# Run the app if script is executed directly
if __name__ == '__main__':
    app.run(port=5555, debug=True)  # Start Flask server on port 5555 with debug mode enabled
