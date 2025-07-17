from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://meal_planner_db_wzy6_user:O4ahEhjZtIOz7sh5Wx3VT16SD9L74sVx@dpg-d1si3r3ipnbc73e4e76g-a/meal_planner_db_wzy6'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models directly here (don't import from app.py)
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200))
    cook_time = db.Column(db.Integer)
    ingredients = db.relationship('Ingredient', backref='meal', cascade="all, delete-orphan")

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully.")


