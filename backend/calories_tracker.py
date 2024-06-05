from flask import Flask, Blueprint, request, jsonify, g
import datetime
import jwt
from config import Config
from functools import wraps
from flasgger import swag_from

app = Flask(__name__)
app.config.from_object(Config)

calories_bp = Blueprint('calories', __name__)

def init_calories_routes(app, mongo):
    users_collection = mongo.db.users
    calories_tracker_collection = mongo.db.calories_tracker
    daily_calories_log_collection = mongo.db.daily_calories_log

    def auth_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({"error": "Bearer token is missing"}), 401
            token = token.split('Bearer ')[1]
            try:
                payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                g.user = payload
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            return f(*args, **kwargs)
        return decorated_function

    @calories_bp.route('/goal', methods=['POST'])
    @auth_required
    @swag_from({
        'tags': ['Calories Tracker'],
        'summary': 'Set a Goal',
        'responses': {
            201: {'description': 'Goal set successfully'},
            400: {'description': 'All fields are required or Invalid username or A goal already exists for the specified period'},
            401: {'description': 'Bearer token is missing or Token has expired or Invalid token'}
        },
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string', 'format': 'date'},
                        'end_date': {'type': 'string', 'format': 'date'},
                        'goal': {'type': 'integer'},
                        'activity': {'type': 'string'}
                    },
                    'required': ['start_date', 'end_date', 'goal', 'activity']
                }
            }
        ],
        'security': [{'Bearer': []}]
    })
    def set_calorie_goal():
        data = request.get_json()
        start_date, end_date, goal, activity = data.get('start_date'), data.get('end_date'), data.get('goal'), data.get('activity')

        if not start_date or not end_date or not goal or not activity:
            return jsonify({"error": "All fields are required"}), 400

        username = g.user['username']
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({"error": "Invalid username"}), 400

        try:
            start_date_obj = datetime.datetime.strptime(start_date, '%d-%m-%Y')
            end_date_obj = datetime.datetime.strptime(end_date, '%d-%m-%Y')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use dd-mm-yyyy."}), 400

        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date_obj < today:
            return jsonify({"error": "Start date cannot be in the past"}), 400

        if end_date_obj <= start_date_obj:
            return jsonify({"error": "End date must be after the start date"}), 400

        if (end_date_obj - start_date_obj).days != 6:
            return jsonify({"error": "The goal period must be exactly 7 days"}), 400

        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')

        overlapping_goal = calories_tracker_collection.find_one({
            'username': username,
            '$or': [
                {'start_date': {'$lte': end_date_str, '$gte': start_date_str}},
                {'end_date': {'$gte': start_date_str, '$lte': end_date_str}},
                {'start_date': {'$lte': start_date_str}, 'end_date': {'$gte': end_date_str}}
            ]
        })

        if overlapping_goal:
            return jsonify({"error": "A goal already exists for the specified period"}), 400

        goal_data = {
            'username': username,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'goal': goal,
            'activity': activity,
            'calories_burned': 0,
            'created_at': datetime.datetime.utcnow().strftime('%Y-%m-%d')
        }
        calories_tracker_collection.insert_one(goal_data)
        return jsonify({"message": "Goal set successfully"}), 201

    @calories_bp.route('', methods=['POST'])
    @auth_required
    @swag_from({
        'tags': ['Calories Tracker'],
        'summary': 'Add Calories by date',
        'description': 'Log the calories consumed for a specific date and update the calorie goal progress.',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'date': {'type': 'string', 'format': 'date', 'description': 'Date of the logged calories (dd-mm-yyyy)'},
                        'calories': {'type': 'number', 'description': 'Number of calories consumed for the date'}
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Calories logged successfully. If the goal is achieved, the message includes goal achievement.',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'description': 'Success message, may include goal achievement notification'}
                    }
                }
            },
            400: {
                'description': 'Bad request or invalid data provided. Error message will be provided in the response.'
            },
            401: {
                'description': 'Bearer token is missing or Token has expired or Invalid token. Authentication required.'
            }
        },
        'security': [{'Bearer': []}]
    })
    def log_calories():
        data = request.get_json()
        date, calories = data.get('date'), data.get('calories')

        if not date or not calories:
            return jsonify({"error": "All fields are required"}), 400

        username = g.user['username']
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({"error": "Invalid username"}), 400

        log_date = datetime.datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        goal = calories_tracker_collection.find_one({'username': username, 'start_date': {'$lte': log_date}, 'end_date': {'$gte': log_date}})

        if not goal:
            return jsonify({"error": "No active goal for this period"}), 400

        # Check if there's already an entry for the date
        existing_log = next((entry for entry in goal.get('calories_logs', []) if entry['date'] == log_date), None)

        if existing_log:
            new_calories_burned = goal['calories_burned'] - existing_log['calories'] + calories
            calories_tracker_collection.update_one(
                {'_id': goal['_id'], 'calories_logs.date': log_date},
                {'$set': {'calories_logs.$.calories': calories}}
            )
        else:
            new_calories_burned = goal['calories_burned'] + calories
            new_log_entry = {'date': log_date, 'calories': calories}
            calories_tracker_collection.update_one(
                {'_id': goal['_id']},
                {'$push': {'calories_logs': new_log_entry}}
            )

        # Update the total calories burned
        calories_tracker_collection.update_one(
            {'_id': goal['_id']},
            {'$set': {'calories_burned': new_calories_burned}}
        )

        message = "Calories logged successfully"
        if new_calories_burned >= goal['goal']:
            message += " & The goal is achieved, Congratulations!"

        return jsonify({"message": message}), 200

    @calories_bp.route('/progress', methods=['GET'])
    @auth_required
    @swag_from({
        'tags': ['Calories Tracker'],
        'summary': 'Get Progress',
        'description': 'Retrieve progress towards the calorie goal for all periods.',
        'responses': {
            200: {
                'description': 'Progress retrieved successfully. Returns progress details for all periods.',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'goal': {'type': 'number', 'description': 'Target calorie goal for the period'},
                            'calories_burned': {'type': 'number', 'description': 'Total calories burned for the period'},
                            'activity': {'type': 'string', 'description': 'Description of the activity related to the goal'},
                            'start_date': {'type': 'string', 'format': 'date', 'description': 'Start date of the period'},
                            'end_date': {'type': 'string', 'format': 'date', 'description': 'End date of the period'}
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request or invalid data provided. Error message will be provided in the response.'
            },
            401: {
                'description': 'Bearer token is missing or Token has expired or Invalid token. Authentication required.'
            }
        },
        'security': [{'Bearer': []}]
    })
    def get_progress():
        username = g.user['username']
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({"error": "Invalid username"}), 400

        goals = list(calories_tracker_collection.find({'username': username}))

        if not goals:
            return jsonify({"error": "No active goals found"}), 400

        progress_list = [
            {
                'goal': goal['goal'],
                'calories_burned': goal['calories_burned'],
                'activity': goal['activity'],
                'start_date': goal['start_date'],
                'end_date': goal['end_date']
            } for goal in goals
        ]

        return jsonify(progress_list), 200

    @calories_bp.route('', methods=['GET'])
    @auth_required
    @swag_from({
        'tags': ['Calories Tracker'],
        'summary': 'Get Calories by Date',
        'description': 'Retrieve the number of calories logged for a specific date.',
        'parameters': [
            {
                'name': 'date',
                'in': 'query',
                'required': True,
                'type': 'string',
                'format': 'date',
                'description': 'Date for which to retrieve logged calories (dd-mm-yyyy)'
            }
        ],
        'responses': {
            200: {
                'description': 'Calories retrieved successfully. Returns the number of calories logged for the specified date.',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'date': {'type': 'string', 'format': 'date', 'description': 'Date for which calories are retrieved'},
                        'calories': {'type': 'number', 'description': 'Number of calories logged for the specified date'}
                    }
                }
            },
            400: {
                'description': 'Bad request or invalid data provided. Error message will be provided in the response.'
            },
            401: {
                'description': 'Bearer token is missing or Token has expired or Invalid token. Authentication required.'
            }
        },
        'security': [{'Bearer': []}]
    })
    def get_calories_by_date():
        date = request.args.get('date')

        if not date:
            return jsonify({"error": "Date is required"}), 400

        username = g.user['username']
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({"error": "Invalid username"}), 400

        try:
            log_date = datetime.datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use dd-mm-yyyy."}), 400

        goal = calories_tracker_collection.find_one({
            'username': username,
            'start_date': {'$lte': log_date},
            'end_date': {'$gte': log_date}
        })

        if not goal:
            return jsonify({"error": "No active goal for this period"}), 400

        daily_log = next((entry for entry in goal.get('calories_logs', []) if entry['date'] == log_date), None)

        if not daily_log:
            return jsonify({"error": "No calories logged for this date"}), 400

        return jsonify({"date": log_date, "calories": daily_log['calories']}), 200
    
    @calories_bp.route('', methods=['DELETE'])
    @auth_required
    @swag_from({
        'tags': ['Calories Tracker'],
        'summary': 'Delete Calories by Date',
        'description': 'Delete the calories logged for a specific date.',
        'parameters': [
            {
                'name': 'date',
                'in': 'query',
                'required': True,
                'type': 'string',
                'format': 'date',
                'description': 'Date for which to delete logged calories (dd-mm-yyyy)'
            }
        ],
        'responses': {
            200: {'description': 'Calories log deleted successfully.'},
            400: {'description': 'Bad request or invalid data provided.'},
            401: {'description': 'Bearer token is missing or Token has expired or Invalid token.'}
        },
        'security': [{'Bearer': []}]
    })
    def delete_calories_by_date():
        date = request.args.get('date')

        if not date:
            return jsonify({"error": "Date is required"}), 400

        username = g.user['username']
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({"error": "Invalid username"}), 400

        try:
            log_date = datetime.datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use dd-mm-yyyy."}), 400

        goal = calories_tracker_collection.find_one({
            'username': username,
            'start_date': {'$lte': log_date},
            'end_date': {'$gte': log_date}
        })

        if not goal:
            return jsonify({"error": "No active goal for this period"}), 400

        updated_logs = [entry for entry in goal.get('calories_logs', []) if entry['date'] != log_date]

        if len(updated_logs) == len(goal.get('calories_logs', [])):
            return jsonify({"error": "No calories logged for this date"}), 400

        new_calories_burned = sum(entry['calories'] for entry in updated_logs)

        calories_tracker_collection.update_one(
            {'_id': goal['_id']},
            {'$set': {'calories_logs': updated_logs, 'calories_burned': new_calories_burned}}
        )

        return jsonify({"message": "Calories log deleted successfully"}), 200

    @calories_bp.route('/goals', methods=['DELETE'])
    @auth_required
    @swag_from({
        'tags': ['Calories Tracker'],
        'summary': 'Delete goals',
        'description': 'Delete a calorie goal for a specified period.',
        'parameters': [
            {
                'name': 'start_date',
                'in': 'query',
                'required': True,
                'type': 'string',
                'format': 'date',
                'description': 'Start date of the goal period (dd-mm-yyyy)'
            },
            {
                'name': 'end_date',
                'in': 'query',
                'required': True,
                'type': 'string',
                'format': 'date',
                'description': 'End date of the goal period (dd-mm-yyyy)'
            }
        ],
        'responses': {
            200: {'description': 'Goal deleted successfully.'},
            400: {'description': 'Bad request or invalid data provided.'},
            401: {'description': 'Bearer token is missing or Token has expired or Invalid token.'}
        },
        'security': [{'Bearer': []}]
    })
    def delete_goal():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"error": "Start date and End date are required"}), 400

        username = g.user['username']
        user = users_collection.find_one({'username': username})
        if not user:
            return jsonify({"error": "Invalid username"}), 400

        try:
            start_date_str = datetime.datetime.strptime(start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            end_date_str = datetime.datetime.strptime(end_date, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use dd-mm-yyyy."}), 400

        goal = calories_tracker_collection.find_one({
            'username': username,
            'start_date': start_date_str,
            'end_date': end_date_str
        })

        if not goal:
            return jsonify({"error": "No goal found for this period"}), 400

        calories_tracker_collection.delete_one({'_id': goal['_id']})

        return jsonify({"message": "Goal deleted successfully"}), 200
    
    app.register_blueprint(calories_bp, url_prefix='/calories')

if __name__ == "__main__":
    from flask_pymongo import PyMongo
    app.config["MONGO_URI"] = Config.MONGO_URI
    mongo = PyMongo(app)
    init_calories_routes(app, mongo)
    app.run(debug=True)