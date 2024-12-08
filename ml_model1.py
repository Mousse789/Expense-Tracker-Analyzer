from fastapi import FastAPI, HTTPException
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Input
from models import get_expenses_by_user_id

app = FastAPI()

# Helper function to fetch and prepare expenses
def fetch_expense_data(user_id: str):
    expenses = get_expenses_by_user_id(user_id)
    if not expenses:
        raise HTTPException(status_code=404, detail=f"No expenses found for user {user_id}")

    # Load expenses into a DataFrame
    df = pd.DataFrame(expenses)

    # Convert 'date' to datetime and filter valid rows
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date')

    # Ensure 'amount' is numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])  # Drop rows with missing 'amount'

    # Select only necessary columns
    df = df[['date', 'amount']]  # Exclude '_id', 'category', etc.

    # print(f"Cleaned DataFrame for user {user_id}:\n{df}") # used for debug
    return df

# LSTM Training
def train_lstm_model(user_id: str):
    data = fetch_expense_data(user_id)
    if data.empty or data.shape[0] < 2:
        return None, None

    # Set 'date' as the index
    data.set_index('date', inplace=True)

    # Resample and sum the 'amount' column only
    numeric_data = data.resample('ME').sum()  # 'ME' for month-end frequency

    # Normalize data using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(numeric_data)

    # Prepare data for LSTM
    X, y = [], []
    for i in range(len(scaled_data) - 1):
        X.append(scaled_data[i])
        y.append(scaled_data[i + 1])
    X, y = np.array(X), np.array(y)

    if len(X) < 1:
        return None, None

    # Reshape for LSTM input
    X = np.reshape(X, (X.shape[0], 1, X.shape[1]))

    # Define LSTM model
    model = Sequential([
        Input(shape=(X.shape[1], X.shape[2])),  # Explicit Input layer
        LSTM(50, return_sequences=True),
        LSTM(50),
        Dense(1)
    ])
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X, y, epochs=20, batch_size=1, verbose=0)

    return model, scaler

# Predict Next Month's Expenses
def predict_next_month_lstm(user_id: str, model, scaler):
    if not model or not scaler:
        return None

    data = fetch_expense_data(user_id)
    if data.empty:
        return None

    data.set_index('date', inplace=True)
    data = data.resample('ME').sum()

    if data.shape[0] < 1:
        return None

    last_value = data['amount'].values[-1]  # Extract the last value
    # Convert to DataFrame to match the format used during fitting
    scaled_last_value = scaler.transform(pd.DataFrame([[last_value]], columns=['amount']))
    scaled_last_value = np.reshape(scaled_last_value, (1, 1, 1))

    prediction = model.predict(scaled_last_value)
    prediction = scaler.inverse_transform(prediction)
    next_month_prediction = round(float(prediction[0, 0]), 2)

    return next_month_prediction

# Anomaly Detection
# def detect_anomalies(user_id: str):
#     data = fetch_expense_data(user_id)
#     if data.empty:
#         return pd.DataFrame()
#
#     data.set_index('date', inplace=True)
#     data = data.resample('M').sum()
#
#     if data.shape[0] < 2:
#         return pd.DataFrame()
#
#     model = IsolationForest(contamination=0.1)
#     data['anomaly'] = model.fit_predict(data[['amount']])
#     anomalies = data[data['anomaly'] == -1].drop(columns=['anomaly'])
#
#     return anomalies


# Savings Plan Recommendation
def recommend_savings_plan(user_id: str):
    data = fetch_expense_data(user_id)
    if data.empty or data.shape[0] < 2:
        return None

    model = NearestNeighbors(n_neighbors=1)
    model.fit(data[['amount']])

    last_amount = data['amount'].values[-1]
    recommendation = model.kneighbors([[last_amount]], return_distance=False)
    recommended_amount = data.iloc[recommendation[0][0]]['amount']

    return recommended_amount

# Autoencoder Training
# def train_autoencoder(user_id: str):
#     data = fetch_expense_data(user_id)
#     if data.empty:
#         return None
#
#     data.set_index('date', inplace=True)
#     data = data.resample('M').sum()
#
#     if data.shape[0] < 2:
#         return None
#
#     scaler = MinMaxScaler()
#     scaled_data = scaler.fit_transform(data)
#
#     input_dim = scaled_data.shape[1]
#     encoding_dim = input_dim // 2
#
#     input_layer = Input(shape=(input_dim,))
#     encoder = Dense(encoding_dim, activation="tanh")(input_layer)
#     decoder = Dense(input_dim, activation="linear")(encoder)
#     autoencoder = Model(inputs=input_layer, outputs=decoder)
#     autoencoder.compile(optimizer='adam', loss='mean_squared_error')
#     autoencoder.fit(scaled_data, scaled_data, epochs=50, batch_size=8, shuffle=True, verbose=2)
#
#     return autoencoder, scaler
#
#
# # Cluster Expenses
# def cluster_expenses(user_id: str, method='kmeans', n_clusters=3):
#     data = fetch_expense_data(user_id)
#     if data.empty or 'amount' not in data.columns or 'description' not in data.columns:
#         return None
#
#     data = data[data['description'].str.strip() != '']
#
#     tfidf = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = tfidf.fit_transform(data['description'])
#
#     lda = LatentDirichletAllocation(n_components=n_clusters, random_state=42)
#     lda_matrix = lda.fit_transform(tfidf_matrix)
#
#     data['sentiment'] = data['description'].apply(lambda x: TextBlob(x).sentiment.polarity)
#
#     combined_features = np.hstack((data[['amount']].values, lda_matrix, data[['sentiment']].values.reshape(-1, 1)))
#
#     if method == 'kmeans':
#         model = KMeans(n_clusters=n_clusters, random_state=42)
#     elif method == 'hierarchical':
#         model = AgglomerativeClustering(n_clusters=n_clusters)
#     elif method == 'dbscan':
#         model = DBSCAN(eps=0.5, min_samples=2)
#     else:
#         raise ValueError(f"Unknown method: {method}")
#
#     data['cluster'] = model.fit_predict(combined_features)
#
#     return data


# FastAPI Routes
@app.get("/train_lstm/{user_id}")
def train_lstm(user_id: str):
    model, scaler = train_lstm_model(user_id)
    if not model:
        raise HTTPException(status_code=400, detail="Failed to train LSTM model")
    return {"message": "LSTM model trained successfully"}

@app.get("/predict_next_month/{user_id}")
def predict_next_month(user_id: str):
    model, scaler = train_lstm_model(user_id)
    if not model:
        raise HTTPException(status_code=400, detail="Failed to train LSTM model")
    prediction = predict_next_month_lstm(user_id, model, scaler)
    if prediction is None:
        raise HTTPException(status_code=400, detail="Failed to predict next month's expenses")
    return {"next_month_prediction": prediction}
