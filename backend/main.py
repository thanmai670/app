from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import bcrypt, jwt, datetime, re
from flasgger import Swagger
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
users_collection = mongo.db.users


swagger = Swagger(app)
CORS(app)  # Enable CORS for all routes

@app.route('/registration', methods=['POST'])
def create_user():
    """Register a new user.
    ---
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            username:
              type: string
              description: Username for registration.
            password:
              type: string
              description: Password for registration.
            email:
              type: string
              description: Email for registration.
            age:
              type: integer
              description: Age for registration.
        required:
          - username
          - password
          - email
          - age
    responses:
      201:
        description: User created successfully.
      400:
        description: Error message if registration fails.
    """
    data = request.get_json()
    data = request.get_json(force=True)
    username, password, email, age = data.get('username'), data.get('password'), data.get('email'), data.get('age')
    if not username or not password or not email or age is None:
        return jsonify({"error": "Username, password, email, and age are required"}), 400
    
    if  int(age) < 18:
        return jsonify({"error": "You must be 18 or older to register"}), 400
    
    if len(password) < 8 or not re.search("[0-9]", password) or not re.search("[!@#$%^&*]", password):
        return jsonify({"error": "Password must be at least 8 characters long and contain at least one special character and one number"}), 400
    
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400
    
    existing_email = users_collection.find_one({'email': email})
    if existing_email:
        return jsonify({"error": "Email already exists"}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {'username': username, 'password': hashed_password, 'email': email, 'age': age, 'created_at': datetime.datetime.utcnow()}
    users_collection.insert_one(user_data)
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Log in to the system.
    ---
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            username:
              type: string
              description: Username for login.
            password:
              type: string
              description: Password for login.
        required:
          - username
          - password
    responses:
      200:
        description: JWT token generated successfully.
      400:
        description: Error message if login fails.
    """
    data = request.get_json()
    data = request.get_json(force=True)
    username, password = data.get('username'), data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 400
    
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24), "sub": "fitnessTrackingSystem"}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        return jsonify({"jwt_token": token}), 200
    
    else:
        return jsonify({"error": "Invalid username or password"}), 400
    

if __name__ == '__main__':
    app.run(debug=True)
