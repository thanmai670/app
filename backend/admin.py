from flask import Blueprint, request, jsonify, g
from bson.objectid import ObjectId
import jwt
from flasgger import swag_from

admin_bp = Blueprint('admin', __name__)

def init_admin_routes(app, mongo):
    exercises_collection = mongo.db.exercises
    body_parts_collection = mongo.db.bodyParts
    sessions_collection = mongo.db.sessions
    users_collection = mongo.db.users

    @admin_bp.before_request
    def authenticate_admin():
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Bearer token is missing"}), 401
        token = token.split('Bearer ')[1]
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            session = sessions_collection.find_one({'username': payload['username'], 'tokens': token})
            if not session or payload.get('hasRole') != 'admin':
                return jsonify({"error": "Unauthorized access"}), 401
            g.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

    @admin_bp.route('/exercises', methods=['POST'])
    @swag_from({
        "tags": ["Admin"],
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "youtube_link": {"type": "string"},
                        "bodyPart": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["name", "youtube_link", "bodyPart", "description"]
                }
            }
        ],
        "responses": {
            "201": {
                "description": "Exercise added successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "id": {"type": "string"}
                    }
                }
            },
            "400": {"description": "Missing required fields"},
            "401": {"description": "Unauthorized access or invalid token"},
            "404": {"description": "Body part not found"}
        }
    })
    def add_exercise():
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401

        data = request.get_json()
        required_fields = ['name', 'youtube_link', 'bodyPart', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        body_part_document = body_parts_collection.find_one({'name': data['bodyPart']})
        if not body_part_document:
            return jsonify({"error": "Body part not found"}), 404

        exercise = {
            "name": data['name'],
            "youtube_link": data['youtube_link'],
            "bodyPart_ref": str(body_part_document['_id']),
            "description": data['description']
        }

        result = exercises_collection.insert_one(exercise)
        return jsonify({"message": "Exercise added successfully"}), 201
    
    @admin_bp.route('/exercises/<string:exercise_id>', methods=['DELETE'])
    @swag_from({
        "tags": ["Admin"],
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "exercise_id",
                "in": "path",
                "type": "string",
                "required": True,
                "description": "The ID of the exercise to delete"
            }
        ],
        "responses": {
            "200": {"description": "Exercise deleted successfully"},
            "401": {"description": "Unauthorized access or invalid token"},
            "404": {"description": "Exercise not found"}
        }
    })
    def delete_exercise(exercise_id):
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401

        result = exercises_collection.delete_one({'_id': ObjectId(exercise_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Exercise not found"}), 404

        return jsonify({"message": "Exercise deleted successfully"}), 200
    
    @admin_bp.route('/exercises/<string:exercise_id>', methods=['PUT'])
    @swag_from({
        "tags": ["Admin"],
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "exercise_id",
                "in": "path",
                "type": "string",
                "required": True,
                "description": "The ID of the exercise to edit"
            },
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "youtube_link": {"type": "string"},
                        "bodyPart": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["name", "youtube_link", "bodyPart", "description"]
                }
            }
        ],
        "responses": {
            "200": {
                "description": "Exercise updated successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                }
            },
            "400": {"description": "Missing required fields"},
            "401": {"description": "Unauthorized access or invalid token"},
            "404": {"description": "Exercise or Body part not found"}
        }
    })
    def edit_exercise(exercise_id):
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401

        data = request.get_json()
        required_fields = ['name', 'youtube_link', 'bodyPart', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        body_part_document = body_parts_collection.find_one({'name': data['bodyPart']})
        if not body_part_document:
            return jsonify({"error": "Body part not found"}), 404

        update = {
            "name": data['name'],
            "youtube_link": data['youtube_link'],
            "bodyPart_ref": str(body_part_document['_id']),
            "description": data['description']
        }

        result = exercises_collection.update_one({'_id': ObjectId(exercise_id)}, {'$set': update})
        if result.matched_count == 0:
            return jsonify({"error": "Exercise not found"}), 404

        return jsonify({"message": "Exercise updated successfully"}), 200
    
    @admin_bp.route('/users', methods=['GET'])
    @swag_from({
        "tags": ["Admin"],
        "summary": "View all users",
        "security": [{"Bearer": []}],
        "responses": {
            "200": {
                "description": "A list of users",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "hasRole": {"type": "string"}
                        }
                    }
                }
            },
            "401": {"description": "Unauthorized access or invalid token"}
        }
    })
    def get_all_users():
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401

        users = list(users_collection.find({}, {'password': 0}))  # Exclude password field
        for user in users:
            user['_id'] = str(user['_id'])
        return jsonify(users), 200

    @admin_bp.route('/loggedusers', methods=['GET'])
    @swag_from({
        "tags": ["Admin"],
        "summary": "View all logged in users",
        "security": [{"Bearer": []}],
        "responses": {
            "200": {
                "description": "List of logged-in users",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "hasRole": {"type": "string"}
                        }
                    }
                }
            },
            "401": {"description": "Unauthorized access or invalid token"}
        }
    })
    def get_logged_in_users():
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401
        
        active_sessions = sessions_collection.find({}, {'_id': 0, 'username': 1})
        logged_in_users = []

        for session in active_sessions:
            user = users_collection.find_one({'username': session['username']}, {'_id': 1, 'username': 1, 'email': 1, 'hasRole': 1})
            if user:
                user['_id'] = str(user['_id'])  # Convert ObjectId to string
                logged_in_users.append(user)

        return jsonify(logged_in_users), 200
    
    @admin_bp.route('/users/<string:user_id>', methods=['PUT'])
    @swag_from({
        "tags": ["AdminManageUser"],
        "summary": "Update user details",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "type": "string",
                "description": "The ID of the user to update"
            },
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "new_username": {"type": "string"},
                        "email": {"type": "string"},
                        "age": {"type": "integer"}
                    },
                    "required": ["new_username", "email", "age"]
                }
            }
        ],
        "responses": {
            "200": {
                "description": "User updated successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                }
            },
            "400": {"description": "Invalid input data"},
            "401": {"description": "Unauthorized access or invalid token"},
            "404": {"description": "User not found"}
        }
    })
    def update_user(user_id):
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401

        data = request.get_json()
        update_data = {}
        if 'email' in data:
            update_data['email'] = data['email']
        if 'age' in data:
            update_data['age'] = data['age']
        if 'new_username' in data:
            update_data['username'] = data['new_username']

        if not update_data:
            return jsonify({"error": "Invalid input data"}), 400

        result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User updated successfully"}), 200
    
    @admin_bp.route('/users/<string:user_id>', methods=['DELETE'])
    @swag_from({
        "tags": ["Admin"],
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "string",
                "required": True,
                "description": "The ID of the user to delete"
            }
        ],
        "responses": {
            "200": {"description": "User deleted successfully"},
            "401": {"description": "Unauthorized access or invalid token"},
            "404": {"description": "User not found"}
        }
    })
    def delete_user(user_id):
        if not hasattr(g, 'user'):
            return jsonify({"error": "Unauthorized access"}), 401

        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200

    app.register_blueprint(admin_bp, url_prefix='/admin')
    
