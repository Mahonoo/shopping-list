from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict

app = Flask(__name__)

# SQLite database file (in the project folder)
import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Meal model
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200))  # e.g., "vegetarian,protein,easy"
    cook_time = db.Column(db.Integer)  # in minutes
    ingredients = db.relationship('Ingredient', backref='meal', cascade="all, delete-orphan")

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)

# ------------------- Routes -------------------

@app.route('/')
def home():
    meals = Meal.query.all()
    return render_template('index.html', meals=meals)

@app.route('/add', methods=['GET', 'POST'])
def add_meal():
    if request.method == 'POST':
        name = request.form['meal_name'].strip()
        cook_time = request.form.get('cook_time', type=int)
        tags = request.form.get('tags', '').strip()

        new_meal = Meal(name=name, cook_time=cook_time, tags=tags)
        db.session.add(new_meal)
        db.session.commit()

        for i in range(10):
            ing_name = request.form.get(f'ingredient_name_{i}')
            qty = request.form.get(f'ingredient_qty_{i}')
            unit = request.form.get(f'ingredient_unit_{i}')

            if ing_name and qty:
                ingredient = Ingredient(
                    name=ing_name.strip(),
                    quantity=float(qty),
                    unit=unit.strip() if unit else None,
                    meal_id=new_meal.id
                )
                db.session.add(ingredient)

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_meal.html')

@app.route('/edit/<int:meal_id>', methods=['GET', 'POST'])
def edit_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)

    if request.method == 'POST':
        meal.name = request.form['meal_name'].strip()
        meal.cook_time = request.form.get('cook_time', type=int)
        meal.tags = request.form.get('tags', '').strip()

        Ingredient.query.filter_by(meal_id=meal.id).delete()

        for i in range(10):
            ing_name = request.form.get(f'ingredient_name_{i}')
            qty = request.form.get(f'ingredient_qty_{i}')
            unit = request.form.get(f'ingredient_unit_{i}')

            if ing_name and qty:
                new_ingredient = Ingredient(
                    name=ing_name.strip(),
                    quantity=float(qty),
                    unit=unit.strip() if unit else None,
                    meal_id=meal.id
                )
                db.session.add(new_ingredient)

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit_meal.html', meal=meal)

@app.route('/delete/<int:meal_id>', methods=['POST'])
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/plan', methods=['GET', 'POST'])
def plan_meals():
    meals = Meal.query.all()
    shopping_list = []

    if request.method == 'POST':
        selected_ids = request.form.getlist('meal_ids')
        ingredients = Ingredient.query.filter(Ingredient.meal_id.in_(selected_ids)).all()

        combined = defaultdict(lambda: {
            'quantity': 0,
            'unit': '',
            'name': '',
            'category': 'Other'
        })

        category_keywords = {
            'Dairy': ['milk', 'cheese', 'butter', 'yogurt', 'cream'],
            'Produce': ['carrot', 'onion', 'garlic', 'pepper', 'lettuce', 'tomato', 'spinach'],
            'Meat': ['chicken', 'beef', 'pork', 'bacon', 'lamb'],
            'Bakery': ['bread', 'roll', 'bun'],
            'Pantry': ['rice', 'pasta', 'oil', 'flour', 'sugar', 'salt', 'spice']
        }

        for ing in ingredients:
            key = ing.name.lower().strip()
            combined[key]['name'] = ing.name.strip()
            combined[key]['quantity'] += ing.quantity
            combined[key]['unit'] = ing.unit or ''

            for category, keywords in category_keywords.items():
                if any(word in key for word in keywords):
                    combined[key]['category'] = category
                    break

        shopping_list = sorted(combined.values(), key=lambda x: x['category'])

    return render_template('plan.html', meals=meals, shopping_list=shopping_list)

# ------------------- App Start -------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
