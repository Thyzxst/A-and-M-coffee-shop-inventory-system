# Importing necessary modules
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

# Initializing Flask app
app = Flask(__name__)
app.secret_key = 'MAYANEKA_04'  # Secret key for session management

# Defining the path to the SQLite database file
DATABASE = os.path.join(os.path.dirname(__file__), 'inventory.db')

# Function to establish a connection to the database
def get_connection():
    return sqlite3.connect(DATABASE)

# Function to initialize the database with schema defined in schema.sql
# Function to initialize the database with schema defined in schema.sql
def init_db():
    with get_connection() as db:
        cursor = db.cursor()
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_items'")
        table_exists = cursor.fetchone()
        if not table_exists:
            # If the table doesn't exist, create it
            with open('schema.sql', 'r') as f:
                db.executescript(f.read())


# Function to fetch all records from the database
def fetch_all(query, params=None):
    with get_connection() as db:
        cursor = db.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

# Function to execute a query on the database
def execute_query(query, params=None):
    with get_connection() as db:
        cursor = db.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        db.commit()

# Route for the home page
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('view_inventory'))
    return redirect(url_for('login'))

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('view_inventory'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder authentication logic
        if username == 'BABAB' and password == 'Amethyst_04':
            session['username'] = username
            return redirect(url_for('view_inventory'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# Route to display inventory
@app.route('/inventory')
def view_inventory():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetching all inventory items from the database
    inventory_items = fetch_all("SELECT * FROM inventory_items")
    
    return render_template('inventory.html', inventory_items=enumerate(inventory_items, start=1))

# Route to add an inventory item
@app.route('/add_inventory_item', methods=['POST'])
def add_inventory_item():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form.get('category')  # Add category field
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')

        if category and name and stock and price:  # Check if category is provided
            try:
                price = int(price)
                stock = int(stock)
            except ValueError:
                flash('Price and Stock must be valid numbers', 'error')
                return redirect(url_for('view_inventory'))

            # Inserting the new inventory item into the database
            execute_query("INSERT INTO inventory_items (category, name, description, price, stock) VALUES (?, ?, ?, ?, ?)",
                          (category, name, description, price, stock))
        else:
            flash('Category, Name, Price, and Stock are required fields', 'error')

    return redirect(url_for('view_inventory'))

# Route to update an inventory item
@app.route('/update_inventory_item/<int:item_id>', methods=['POST'])
@app.route('/update_inventory_item/<int:item_id>', methods=['POST'])
def update_inventory_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form.get('category')
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')

        # Construct the update query based on the filled fields
        update_query = "UPDATE inventory_items SET "
        params = []
        if category:
            update_query += "category=?, "
            params.append(category)
        if name:
            update_query += "name=?, "
            params.append(name)
        if description:
            update_query += "description=?, "
            params.append(description)
        if price:
            try:
                price = int(price)
                update_query += "price=?, "
                params.append(price)
            except ValueError:
                flash('Price must be a valid number', 'error')
                return redirect(url_for('view_inventory'))
        if stock:
            update_query += "stock=?, "
            params.append(stock)

        # Remove the trailing comma and space from the query
        update_query = update_query[:-2]

        # Add the WHERE clause to specify the item_id
        update_query += " WHERE id=?"

        # Append item_id to the params list
        params.append(item_id)

        # Execute the update query
        execute_query(update_query, params)

    return redirect(url_for('view_inventory'))

# Route to delete an inventory item
@app.route('/delete_inventory_item/<int:item_id>', methods=['POST'])
def delete_inventory_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Deleting the inventory item from the database
    execute_query("DELETE FROM inventory_items WHERE id=?", (item_id,))
    
    return redirect(url_for('view_inventory'))

# Running the Flask app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
