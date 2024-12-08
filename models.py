# import sqlite3
# import os

# # Create a new SQLite database connection
# def create_connection():
#     conn = None
#     try:
#         conn = sqlite3.connect('personal_finance.db')
#     except sqlite3.Error as e:
#         print(e)
#     return conn

# # Initialize the database
# def init_db():
#     conn = create_connection()
#     with conn:
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT UNIQUE NOT NULL,
#                 password TEXT NOT NULL,
#                 profile_image TEXT
#             )
#         ''')
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS expenses (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 category TEXT NOT NULL,
#                 amount REAL NOT NULL,
#                 date TEXT NOT NULL,
#                 description TEXT,
#                 FOREIGN KEY (user_id) REFERENCES users (id)
#             )
#         ''')
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS goals (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 goal TEXT NOT NULL,
#                 target_amount REAL NOT NULL,
#                 current_amount REAL NOT NULL,
#                 FOREIGN KEY (user_id) REFERENCES users (id)
#             )
#         ''')
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS income (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 source TEXT NOT NULL,
#                 amount REAL NOT NULL,
#                 date TEXT NOT NULL,
#                 FOREIGN KEY (user_id) REFERENCES users (id)
#             )
#         ''')
#         conn.execute('''
#             CREATE TABLE IF NOT EXISTS recurring_expenses (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 category TEXT NOT NULL,
#                 amount REAL NOT NULL,
#                 frequency TEXT NOT NULL, -- e.g., daily, weekly, monthly
#                 next_due_date TEXT NOT NULL,
#                 FOREIGN KEY (user_id) REFERENCES users (id)
#             )
#         ''')
#         conn.execute('''
#                   CREATE TABLE IF NOT EXISTS recurring_expenses (
#                       id INTEGER PRIMARY KEY AUTOINCREMENT,
#                       user_id INTEGER NOT NULL,
#                       category TEXT NOT NULL,
#                       amount REAL NOT NULL,
#                       frequency TEXT NOT NULL, -- e.g., daily, weekly, monthly
#                       next_due_date TEXT NOT NULL,
#                       FOREIGN KEY (user_id) REFERENCES users (id)
#                   )
#               ''')
#     conn.close()
# def add_description_column():
#     conn = create_connection()
#     try:
#         with conn:
#             conn.execute('ALTER TABLE expenses ADD COLUMN description TEXT')
#     except sqlite3.OperationalError as e:
#         if 'duplicate column name: description' not in str(e):
#             print(e)
#     finally:
#         conn.close()
# def add_profile_image_column():
#     conn = create_connection()
#     try:
#         with conn:
#             conn.execute('ALTER TABLE users ADD COLUMN profile_image TEXT')
#     except sqlite3.OperationalError as e:
#         if 'duplicate column name: profile_image' not in str(e):
#             raise
#     finally:
#         conn.close()

# # Call this function to apply the schema change
# add_profile_image_column()

# def get_user_by_username(username):
#     conn = create_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM users WHERE username = ?', (username,))
#     user = cur.fetchone()
#     conn.close()
#     return user

# def create_user(username, password):
#     conn = create_connection()
#     try:
#         with conn:
#             conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
#         return True
#     except sqlite3.IntegrityError:
#         return False

# def create_income(user_id, source, amount, date):
#     conn = create_connection()
#     with conn:
#         conn.execute('INSERT INTO income (user_id, source, amount, date) VALUES (?, ?, ?, ?)', (user_id, source, amount, date))
#     conn.close()

# def get_income_by_user_id(user_id):
#     conn = create_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM income WHERE user_id = ?', (user_id,))
#     income = cur.fetchall()
#     conn.close()
#     return income

# def get_expenses_fortbl_by_user_id(user_id):
#     conn = create_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM expenses WHERE user_id = ?', (user_id,))
#     expenses = cur.fetchall()
#     conn.close()
#     return expenses

# def create_expense(user_id, category, amount, date, description):
#     conn = create_connection()
#     with conn:
#         conn.execute('INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)', (user_id, category, amount, date, description))
#     conn.close()

# def get_goals_by_user_id(user_id):
#     conn = create_connection()
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM goals WHERE user_id = ?', (user_id,))
#     goals = cur.fetchall()
#     conn.close()
#     return goals

# def create_goal(user_id, goal, target_amount, current_amount):
#     conn = create_connection()
#     with conn:
#         conn.execute('''
#             INSERT INTO goals (user_id, goal, target_amount, current_amount)
#             VALUES (?, ?, ?, ?)
#         ''', (user_id, goal, target_amount, current_amount))
#     conn.close()

# def get_user_by_id(user_id):
#     conn = create_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, username, profile_image FROM users WHERE id = ?", (user_id,))
#     user = cursor.fetchone()
#     conn.close()

#     if user:
#         return {'id': user[0], 'username': user[1], 'profile_image': user[2]}
#     return None

# def update_user_profile(user_id, username, password=None, profile_image=None):
#     conn = create_connection()
#     with conn:
#         if password and profile_image:
#             conn.execute('''
#                 UPDATE users
#                 SET username = ?, password = ?, profile_image = ?
#                 WHERE id = ?
#             ''', (username, password, profile_image, user_id))
#         elif password:
#             conn.execute('''
#                 UPDATE users
#                 SET username = ?, password = ?
#                 WHERE id = ?
#             ''', (username, password, user_id))
#         elif profile_image:
#             conn.execute('''
#                 UPDATE users
#                 SET username = ?, profile_image = ?
#                 WHERE id = ?
#             ''', (username, profile_image, user_id))
#         else:
#             conn.execute('''
#                 UPDATE users
#                 SET username = ?
#                 WHERE id = ?
#             ''', (username, user_id))
#     conn.close()
# def get_expenses_by_user_id(user_id):
#     conn = sqlite3.connect('personal_finance.db')
#     cursor = conn.execute('''
#         SELECT date, amount FROM expenses WHERE user_id = ? ORDER BY date
#     ''', (user_id,))
#     expenses = [{'date': row[0], 'amount': row[1]} for row in cursor.fetchall()]
#     conn.close()
#     return expenses

# def reset_db():
#     db_path = 'personal_finance.db'
#     if os.path.exists(db_path):
#         os.remove(db_path)
#     init_db()



# # Initialize the database
# init_db()
# # Ensure the profile_image column exists
# add_profile_image_column()
# add_description_column()

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.son import SON
import os

# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://ikedinachimugochukwu:kVE8MslMtMYRZqbt@cs531cluster.gxaub.mongodb.net/?retryWrites=true&w=majority&appName=CS531Cluster"
)
db = client.finances

# Initialize MongoDB collections
def init_db():
    collections = ["users", "expenses", "income", "goals", "recurring_expenses"]
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)

# User operations
def create_user(username, password, profile_image=None):
    try:
        db.users.insert_one({
            "username": username,
            "password": password,
            "profile_image": profile_image,
        })
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_user_by_username(username):
    print("get_user_by_username:" , db.users.find_one({"username": username}))
    return db.users.find_one({"username": username})

def get_user_by_id(user_id):
    
    return db.users.find_one({"_id": ObjectId(user_id)})

def update_user_profile(user_id, username=None, password=None, profile_image=None):
    updates = {}
    if username:
        updates["username"] = username
    if password:
        updates["password"] = password
    if profile_image:
        updates["profile_image"] = profile_image

    db.users.update_one({"_id": user_id}, {"$set": updates})

# Expense operations
def create_expense(user_id, category, amount, date, description):
    db.expenses.insert_one({
        "user_id": user_id,
        "category": category,
        "amount": amount,
        "date": date,
        "description":description
    })

def get_expenses_by_user_id(user_id):
    print(user_id, list(db.expenses.find({"user_id": user_id})))
    return list(db.expenses.find({"user_id": user_id}))
def get_all_months(user_id):
    pipeline = [
        {
            "$match": {"user_id": user_id}  # Filter expenses by user_id
        },
        {
            "$addFields": {
                "converted_date": {
                    "$cond": {
                        "if": {"$isArray": "$date"},  # Checks if it's already a valid date
                        "then": "$date",
                        "else": {"$toDate": "$date"}
                    }
                }
            }
        },
        {
            "$addFields": {
                "month": {"$dateToString": {"format": "%Y-%m", "date": "$converted_date"}}
            }
        },
        {
            "$group": {
                "_id": "$month"
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    result = db.expenses.aggregate(pipeline)
    print(result)
    return [doc["_id"] for doc in result]


def get_expenses_by_month(selected_month, user_id):
    pipeline = [
        {
                "$match": {"user_id": user_id}  # Filter expenses by user_id
        },
        {
            # Convert date to proper Date type if it's stored incorrectly
            "$addFields": {
                "converted_date": {"$toDate": "$date"}
            }
        },
        {
            # Extract the month from the date
            "$addFields": {
                "month": {"$dateToString": {"format": "%Y-%m", "date": "$converted_date"}}
            }
        },
        {
            # Filter only for the selected month
            "$match": {"month": selected_month}
        },
        {
            # Group by category
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }
        }
    ]

    result = db.expenses.aggregate(pipeline)
    return [{"category": doc["_id"], "total": doc["total"]} for doc in result]


def get_expenses_fortbl_by_user_id(user_id):
    print(user_id, list(db.expenses.find({"user_id": user_id})), )
    return list(db.expenses.find({"user_id": user_id}))

# Income operations
def create_income(user_id, source, amount, date):
    db.income.insert_one({
        "user_id": user_id,
        "source": source,
        "amount": amount,
        "date": date,
    })

def get_income_by_user_id(user_id):
    return list(db.income.find({"user_id": user_id}))

# Goal operations
def create_goal(user_id, goal, target_amount, current_amount):
    db.goals.insert_one({
        "user_id": user_id,
        "goal": goal,
        "target_amount": target_amount,
        "current_amount": current_amount,
    })

def get_goals_by_user_id(user_id):
    return list(db.goals.find({"user_id": user_id}))

# Recurring expenses operations
def create_recurring_expense(user_id, category, amount, frequency, next_due_date):
    db.recurring_expenses.insert_one({
        "user_id": user_id,
        "category": category,
        "amount": amount,
        "frequency": frequency,
        "next_due_date": next_due_date,
    })

def get_recurring_expenses_by_user_id(user_id):
    return list(db.recurring_expenses.find({"user_id": user_id}))

# Database reset (for testing purposes)
def reset_db():
    collections = ["users", "expenses", "income", "goals", "recurring_expenses"]
    for collection in collections:
        db[collection].delete_many({})

# Initialize the database
init_db()

# Example usage
# if __name__ == "__main__":
#     reset_db()
#     create_user("testuser", "password123", "profile.png")
#     user = get_user_by_username("testuser")
#     user_id = user["_id"]
#     create_expense(user_id, "Food", 15.0, "2024-11-21", "Lunch at a cafe")
#     create_income(user_id, "Job", 2000.0, "2024-11-20")
#     create_goal(user_id, "Save for a car", 15000.0, 5000.0)

#     print(get_user_by_username("testuser"))
#     print(get_expenses_by_user_id(user_id))
#     print(get_income_by_user_id(user_id))
#     print(get_goals_by_user_id(user_id))
