import logging
import os
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, Form, UploadFile, File
from fastapi import Request
from pydantic import BaseModel
from passlib.context import CryptContext
from starlette.responses import HTMLResponse, RedirectResponse
from werkzeug.utils import secure_filename
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

from ml_model import train_lstm_model, \
    predict_next_month_lstm, detect_anomalies, cluster_expenses, recommend_savings_plan, fetch_expense_data, \
    detect_anomalies_autoencoder
from models import get_user_by_username, create_user, create_expense, get_goals_by_user_id, create_goal, get_user_by_id, \
    update_user_profile, create_income, get_income_by_user_id, get_expenses_fortbl_by_user_id

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.secret_key = 'your_secret_key'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
# Configure upload folder
UPLOAD_FOLDER = 'static/profile_images'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

client = MongoClient("mongodb://localhost:27017")
db = client["personal_finance"]  # Replace with your actual DB name
users_collection = db["users"]
expenses_collection = db["expenses"]
goals_collection = db["goals"]
income_collection = db["income"]

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

logging.basicConfig(level=logging.INFO)

# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(request: Request) -> Optional[dict]:
    user_id = request.cookies.get("user_id")  # Retrieve user ID from cookies (or headers, etc.)
    if user_id:
        user = get_user_by_id(user_id)  # Fetch user from database or other storage
        if user:
            return user
    raise HTTPException(status_code=401, detail="Not authenticated")

# def create_connection():
#     try:
#         # Create MongoDB client and connect to the database
#         client = MongoClient(MONGO_URI)
#         db = client[DB_NAME]
#         return db
#     except Exception as e:
#         print(f"Error connecting to MongoDB: {e}")
#         raise HTTPException(status_code=500, detail="Error connecting to the database.")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_id = request.cookies.get('user_id')
    if user_id:
        model, scaler = train_lstm_model(user_id)
        next_month_prediction = predict_next_month_lstm(user_id, model, scaler)
        return templates.TemplateResponse("home.html", {"request": request, "prediction": next_month_prediction})
    return templates.TemplateResponse("home.html", {"request": request})

class LoginForm(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(form_data: LoginForm, request: Request):
    user = get_user_by_username(form_data.username)
    if user and verify_password(form_data.password, user["password"]):
        response = templates.TemplateResponse("home.html", {"request": request})
        response.set_cookie(key="user_id", value=str(user["_id"]))
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

class RegisterForm(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(form_data: RegisterForm, request: Request):
    if get_user_by_username(form_data.username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken"})

    hashed_password = hash_password(form_data.password)
    user = {"username": form_data.username, "password": hashed_password}
    users_collection.insert_one(user)
    return templates.TemplateResponse("login.html", {"request": request, "message": "Registration successful!"})


@app.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("user_id")
    return response


class ExpenseForm(BaseModel):
    category: str
    amount: float
    date: str
    description: str = None

@app.post("/add_expense")
async def add_expense(form_data: ExpenseForm, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please login first"})

    create_expense(user_id, form_data.category, form_data.amount, form_data.date, form_data.description)
    return templates.TemplateResponse("view_expenses.html", {"request": request, "message": "Expense added!"})


@app.get("/view_expenses", response_class=HTMLResponse)
async def view_expenses(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please login first"})

    expenses = await get_expenses_fortbl_by_user_id(user_id)
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found for this user.")
    return templates.TemplateResponse("view_expenses.html", {"request": request, "expenses": expenses})


@app.post("/add_goal", response_class=RedirectResponse)
async def add_goal(request: Request, goal: str = Form(...), target_amount: float = Form(...), current_amount: float = Form(...)):
    user_id = get_current_user(request)  # Get the user_id from session

    # Create the goal and add it to the "database"
    goal_data = {"user_id": user_id, "goal": goal, "target_amount": target_amount, "current_amount": current_amount}
    goals_collection.append(goal_data)  # This simulates saving to a database

    # Redirect the user to view goals after adding the goal
    return RedirectResponse(url="/view_goals", status_code=303)

@app.get("/view_goals", response_class=HTMLResponse)
async def view_goals(request: Request):
    user_id = get_current_user(request)  # Get the user_id from session
    # Retrieve the goals for the current user
    user_goals = [goal for goal in goals_collection if goal["user_id"] == user_id]
    return templates.TemplateResponse("view_goals.html", {"request": request, "goals": user_goals})



@app.get("/profile")
async def profile(request: Request):
    # Simulate fetching the user from cookies (authentication)
    user_id = get_current_user(request)
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.post("/profile")
async def update_profile(request: Request, new_username: str = Form(...), new_password: Optional[str] = Form(None), profile_image: UploadFile = File(None)):
    user_id = get_current_user(request)  # Get user from cookies

    # Fetch current user data
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Handle password update (if new password is provided)
    hashed_password = None
    if new_password:
        hashed_password = pwd_context.hash(new_password)

    # Handle file upload
    filename = None
    if profile_image:
        filename = secure_filename(profile_image.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await profile_image.read())

    # Update user profile
    update_user_profile(user_id, new_username, hashed_password, filename)

    return RedirectResponse(url="/profile", status_code=303)

# Pydantic model to validate the form data
class Income(BaseModel):
    source: str
    amount: float
    date: str

# Endpoint to add income
@app.post("/add_income", response_class=RedirectResponse)
async def add_income(request: Request, source: str = Form(...), amount: float = Form(...), date: str = Form(...)):
    user_id = get_current_user(request)  # Get the user ID from session (cookie or other means)

    # Simulate saving income data (you can replace this with database interaction)
    income_data = {"user_id": user_id, "source": source, "amount": amount, "date": date}
    income_collection.append(income_data)

    # Redirect to the view income page after adding income
    return RedirectResponse(url="/view_income", status_code=303)

# Endpoint to view income
@app.get("/view_income")
async def view_income(request: Request):
    user_id = get_current_user(request)  # Get the user ID from session (cookie or other means)

    # Simulate retrieving income data from the database for a specific user
    user_incomes = [income for income in income_collection if income["user_id"] == user_id]

    # Render the view_income.html template with the incomes
    return templates.TemplateResponse("view_income.html", {"request": request, "income": user_incomes})


@app.get("/predict_expenses")
async def predict_expenses(request: Request):
    user_id = get_current_user(request)  # Authenticate user via cookies

    # Fetch user's expense data
    expenses = fetch_expense_data(user_id)
    if expenses.empty or expenses.shape[0] < 2:  # Check for sufficient historical data
        logging.warning(f"Not enough data available for user {user_id} to make a prediction.")
        return templates.TemplateResponse("predict_expenses.html", {"request": request, "error": "Not enough data available to make a prediction."})

    # Train the LSTM model
    model, scaler = train_lstm_model(user_id)
    if not model or not scaler:
        logging.error(f"Model training failed for user {user_id} due to insufficient data.")
        return templates.TemplateResponse("predict_expenses.html", {"request": request, "error": "Not enough data to train the model."})

    # Make the prediction
    next_month_prediction = predict_next_month_lstm(user_id, model, scaler)
    if next_month_prediction is None:
        logging.error(f"Prediction could not be made for user {user_id}")
        return templates.TemplateResponse("predict_expenses.html", {"request": request, "error": "Not enough data to make a prediction."})

    # Prepare data for rendering
    next_month_prediction = float(next_month_prediction)

    expenses['date'] = pd.to_datetime(expenses['date'])
    expenses.set_index('date', inplace=True)
    expenses = expenses.resample('ME').sum()  # Resample by month-end (ME)
    dates = expenses.index.strftime('%Y-%m').tolist()
    amounts = expenses['amount'].tolist()

    # Add the prediction to the data
    labels = dates + ['Next Month']
    actual_expenses = amounts + [None]
    predicted_expenses = [None] * len(amounts) + [next_month_prediction]

    # Return the template response with the data
    return templates.TemplateResponse("predict_expenses.html", {
        "request": request,
        "prediction": next_month_prediction,
        "labels": labels,
        "actual_expenses": actual_expenses,
        "predicted_expenses": predicted_expenses
    })
# @app.route('/view_anomalies')
# def view_anomalies():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#
#     user_id = session['user_id']
#     anomalies = detect_anomalies(user_id)
#
#     return render_template('view_anomalies.html', anomalies=anomalies)

# @app.route('/detect_anomalies')
# def detect_anomalies_route():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#
#     user_id = session['user_id']
#     anomalies = detect_anomalies(user_id)
#
#     if anomalies is None:
#         logging.error(f"Anomalies could not be detected for user {user_id}")
#         return render_template('detect_anomalies.html', error="Not enough data to detect anomalies.")
#
#     return render_template('detect_anomalies.html', anomalies=anomalies)

# @app.route('/detect_anomalies_autoencoder')
# def detect_anomalies_autoencoder_route():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#
#     user_id = session['user_id']
#     anomalies_autoencoder = detect_anomalies_autoencoder(user_id)
#
#     if anomalies_autoencoder is None:
#         logging.error(f"Anomalies could not be detected using autoencoder for user {user_id}")
#         return render_template('detect_anomalies_autoencoder.html', error="Not enough data to detect anomalies using autoencoder.")
#
#     return render_template('detect_anomalies_autoencoder.html', anomalies=anomalies_autoencoder)

# @app.route('/expense_clusters')
# def view_expense_clusters():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#
#     user_id = session['user_id']
#     try:
#         clustered_data = cluster_expenses(user_id)
#         clustered_data = clustered_data.to_dict(orient='records')  # Convert DataFrame to list of dictionaries
#     except ValueError as e:
#         flash(str(e), 'danger')
#         return redirect(url_for('home'))
#
#     return render_template('view_clusters.html', clustered_data=clustered_data)

@app.get("/recommend_savings")
async def recommend_savings(request: Request):
    # Authenticate user based on cookies (or implement session checking here)
    user_id = get_current_user(request)  # Get the user ID from cookies/session

    # Get the recommended savings amount for the user
    recommended_amount = recommend_savings_plan(user_id)

    # Render the template with the recommended savings amount
    return templates.TemplateResponse("recommend_savings.html", {"request": request, "recommended_amount": recommended_amount})


# @app.route('/expenses/clusters')
# def expense_clusters():
#     if 'user_id' in session:
#         user_id = session['user_id']
#         method = request.args.get('method', 'kmeans')
#         n_clusters = int(request.args.get('n_clusters', 3))
#
#         clustered_data = cluster_expenses(user_id, method=method, n_clusters=n_clusters)
#         if clustered_data is not None:
#             clusters = clustered_data.groupby('cluster').apply(lambda x: x.to_dict(orient='records')).to_dict()
#             return render_template('expense_clusters.html', clusters=clusters, method=method, n_clusters=n_clusters)
#
#         flash('Not enough data for clustering')
#         return redirect(url_for('view_expenses'))
#
#     return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
