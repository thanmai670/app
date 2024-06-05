from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import bcrypt, jwt, datetime, re
from flasgger import Swagger
from flask_cors import CORS
from config import Config
from functools import wraps
from calories_tracker import init_calories_routes
from workouts import init_workouts_routes
from progressTracking import init_progress_routes
from dashboard import init_dashboard_routes
from admin import init_admin_routes


app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
users_collection = mongo.db.users
blacklist_collection = mongo.db.token_blacklist
sessions_collection = mongo.db.sessions

init_calories_routes(app, mongo)
init_workouts_routes(app, mongo)
init_progress_routes(app, mongo)
init_dashboard_routes(app, mongo)
init_admin_routes(app, mongo)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Fitness Tracking System",
        "description": "API to get access to features of Application.",
        "version": "1.0.0"
    },
    "host": "localhost:5000",  
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter 'Bearer' [space] and then your token in the text input below.\n\nExample: 'Bearer 12345abcdef'"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, template=swagger_template)

CORS(app)  

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
    user_data = {'username': username, 'password': hashed_password, 'email': email, 'age': age, 'created_at': datetime.datetime.utcnow(), 'hasRole' : 'default'}
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
    username, password = data.get('username'), data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 400

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        userData = users_collection.find_one({'username' : user['username']})
        print("USERNAME :: ", userData['hasRole'])
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10), "sub": "fitnessTrackingSystem", "hasRole" : userData['hasRole']}, app.config['JWT_SECRET_KEY'], algorithm='HS256')

        session_data = sessions_collection.find_one({'username': username})
        if session_data:
            sessions_collection.update_one(
                {'username': username},
                {'$push': {'tokens': token}}
            )
        else:
            session_data = {
                "username": username,
                "tokens": [token]
            }
            sessions_collection.insert_one(session_data)
        return jsonify({"jwt_token": token}), 200

    else:
        return jsonify({"error": "Invalid username or password"}), 400

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            session_data = sessions_collection.find_one({"username": data['username']})
            if not session_data:
                return jsonify({'message': 'No active session for user {' + data['username'] + '} found!'}), 401
            token_data = sessions_collection.find_one({"tokens": token})
            if not token_data:
                return jsonify({'message': 'Token is invalid '}), 401
            request.user = data['username']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout a user by deleting their session.
    ---
    responses:
      200:
        description: User logged out successfully.
      400:
        description: Error message if logout fails.
    """
    token = request.headers['Authorization'].split(" ")[1]
    try:
        sessions_collection.update_one(
            {"username": request.user},
            {"$pull": {"tokens": token}}
        )
        sessions_collection.delete_one({"username": request.user})
        return jsonify({"message": "User logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
