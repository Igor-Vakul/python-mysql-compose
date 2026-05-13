import random
import os
import mysql.connector
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

main_dishes = ["Spaghetti Carbonara", "Grilled Chicken Caesar Salad", "Vegetable Stir-Fry", "Beef Tacos", "Mushroom Risotto", "Teriyaki Salmon"]
side_dishes = ["Garlic Bread", "Steamed Broccoli", "Roasted Potatoes", "Caprese Salad", "Quinoa Pilaf", "Grilled Asparagus"]
desserts = ["Chocolate Lava Cake", "Fruit Salad", "Cheesecake", "Apple Pie", "Tiramisu", "Ice Cream Sundae"]

def get_complex_dinner_suggestion():
    return random.choice(main_dishes), random.choice(side_dishes), random.choice(desserts)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USERNAME'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DATABASE')
    )

@app.route('/')
def index():
    main, side, dessert = get_complex_dinner_suggestion()
    return render_template('index.html', main=main, side=side, dessert=dessert)

@app.route('/save', methods=['POST'])
def save():
    main = request.form.get('main')
    side = request.form.get('side')
    dessert = request.form.get('dessert')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS suggestions "
        "(id INT AUTO_INCREMENT PRIMARY KEY, main_dish VARCHAR(100), side_dish VARCHAR(100), dessert VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    cursor.execute(
        "INSERT INTO suggestions (main_dish, side_dish, dessert) VALUES (%s, %s, %s)",
        (main, side, dessert)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)