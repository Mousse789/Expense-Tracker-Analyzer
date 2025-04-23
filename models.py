from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.son import SON
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
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
    # print("get_user_by_username:" , db.users.find_one({"username": username}))
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
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})

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
    # print(user_id, list(db.expenses.find({"user_id": user_id})))
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
    # print(user_id, list(db.expenses.find({"user_id": user_id})), )
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


def get_income_months():
    months_cursor = db.income.aggregate([
        {"$addFields": {"converted_date": {"$toDate": "$date"}}},
        {"$addFields": {"month": {"$dateToString": {"format": "%Y-%m", "date": "$converted_date"}}}},
        {"$group": {"_id": "$month"}},
        {"$sort": {"_id": 1}}
    ])
    months_list = [doc["_id"] for doc in months_cursor]
    return months_list



def aggregate_income_by_month_and_category(user_id, selected_month):
    """Aggregate income data by categories filtered by month."""
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$addFields": {"converted_date": {"$toDate": "$date"}}},
        {"$addFields": {"month": {"$dateToString": {"format": "%Y-%m", "date": "$converted_date"}}}},
        {"$match": {"month": selected_month}},
        {
            "$group": {
                "_id": "$source",
                "total": {"$sum": "$amount"}
            }
        }
    ]
    result = list(db.income.aggregate(pipeline))
    return [{"source": record["_id"], "total": record["total"]} for record in result]



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
