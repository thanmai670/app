import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/fitness-tracking')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', '123456.')
