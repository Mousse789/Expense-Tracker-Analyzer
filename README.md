Expense Tracker and Analyzer
Expense Tracker and Analyzer is a comprehensive personal finance management application designed to help users efficiently track, analyze, and manage their expenses. It features a user-friendly GUI, leverages FastAPI for high performance, and utilizes MongoDB for robust data storage. With advanced machine learning algorithms, the app offers insightful expense categorization, predictive analytics, and real-time data processing, empowering users to make informed financial decisions effortlessly.

Key Features:
User Login/Register
The application includes a secure and efficient user authentication system with features for user registration and login. It uses bcrypt to hash and securely store passwords, ensuring robust protection against unauthorized access.
Add/View Expenses
Easily add and categorize expenses with a user-friendly interface. View detailed expense records with date, amount, category, and description.
Monthly Expense Summary Visualization
Modern, responsive design with easy navigation. Visualize your data with clear, informative charts and graphs.
Predict Expenses
Predict future expenses with an LSTM-based model trained on your historical data.
Add/View Income
Record and categorize your income sources.
Recommend Savings
Get personalized savings plan recommendations based on your spending habits.


Technical Highlights:
Backend: FastAPI, MongoDB, TensorFlow, Scikit-learn
Frontend: HTML, CSS, JavaScript
Machine Learning Models: LSTM for expense prediction, MinMaxScaler for data normalization, NearestNeighbors for savings recommendation.

Project Web Application Initialization:
Set up a virtual environment
Create a Virtual Environment: python -m venv venv

Activate the Virtual Environment:
On Linux/macOS: source venv/bin/activate
On Windows: venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt

Run the Application
uvicorn app1:app --reload
App runs on http://127.0.0.1:8000

Expense Tracker and Analyzer is the ultimate tool for anyone looking to gain control over their finances, understand their spending habits, and achieve their financial goals with confidence.
