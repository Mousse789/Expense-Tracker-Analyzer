from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, Input
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from textblob import TextBlob
from models import get_expenses_by_user_id, create_expense

app = FastAPI()

class ExpenseInput(BaseModel):
    user_id: str
    date: datetime
    amount: float
    description: str = None

@app.post("/expenses/")
async def add_expense(expense: ExpenseInput):
    await create_expense(expense.user_id, expense.amount, expense.date, expense.description)
    return {"message": "Expense added successfully"}

@app.get("/expenses/{user_id}")
async def fetch_expense_data(user_id: str):
    expenses = await get_expenses_by_user_id(user_id)
    df = pd.DataFrame(expenses)
    if df.empty:
        raise HTTPException(status_code=404, detail="No expenses found")
    return df.to_dict(orient="records")

async def prepare_data_for_model(user_id: str):
    expenses = await fetch_expense_data(user_id)
    df = pd.DataFrame(expenses)
    if df.empty or df.shape[0] < 2:
        return None, "Not enough data"
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.resample('M').sum()
    return df, "Data prepared"

@app.post("/train_lstm/{user_id}")
async def train_lstm_model(user_id: str):
    df, message = await prepare_data_for_model(user_id)
    if not df:
        return {"message": message}

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[['amount']])
    X, y = [], []
    for i in range(len(scaled_data) - 1):
        X.append(scaled_data[i])
        y.append(scaled_data[i + 1])
    X, y = np.array(X), np.array(y)

    if len(X) < 1:
        return {"message": "Not enough samples"}

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(1, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X, y, epochs=20, batch_size=1, verbose=2)
    # Optionally save the model here
    return {"message": "LSTM model trained successfully"}

@app.get("/predict_next_month/{user_id}")
async def predict_next_month_lstm(user_id: str):
    model, scaler, _ = await train_lstm_model(user_id)  # Modify to return model and scaler as well
    df, _ = await prepare_data_for_model(user_id)
    if not df:
        return {"message": "No data available for prediction"}

    last_value = df['amount'].values[-1]
    scaled_last_value = scaler.transform([[last_value]])
    prediction = model.predict(np.array([scaled_last_value]).reshape(1, 1, 1))
    predicted_amount = scaler.inverse_transform(prediction)[0][0]

    return {"next_month_prediction": predicted_amount}

# @app.get("/detect_anomalies/{user_id}")
# async def detect_anomalies(user_id: str):
#     df, message = await prepare_data_for_model(user_id)
#     if not df:
#         return {"message": message}
#
#     model = IsolationForest(contamination=0.1)
#     df['anomaly'] = model.fit_predict(df[['amount']].values.reshape(-1, 1))
#     anomalies = df[df['anomaly'] == -1]
#     return {"anomalies": anomalies.to_dict(orient='records')}

@app.get("/recommend_savings/{user_id}")
async def recommend_savings_plan(user_id: str):
    df, message = await prepare_data_for_model(user_id)
    if not df:
        return {"message": message}

    model = NearestNeighbors(n_neighbors=1)
    amounts = df['amount'].values.reshape(-1, 1)
    model.fit(amounts)
    last_amount = amounts[-1]
    _, indices = model.kneighbors([last_amount])
    recommended_amount = amounts[indices[0][0]]
    return {"last_amount": float(last_amount), "recommended_savings": float(recommended_amount)}

@app.post("/train_autoencoder/{user_id}")
async def train_autoencoder(user_id: str):
    df = await fetch_expense_data(user_id)
    if df.empty or df.shape[0] < 2:
        return {"message": "Not enough data for training"}

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.resample('M').sum()

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[['amount']])

    input_dim = scaled_data.shape[1]
    encoding_dim = input_dim // 2  # Simple autoencoder structure

    input_layer = Input(shape=(input_dim,))
    encoder = Dense(encoding_dim, activation='relu')(input_layer)
    decoder = Dense(input_dim, activation='sigmoid')(encoder)
    autoencoder = Model(input_layer, decoder)
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    autoencoder.fit(scaled_data, scaled_data, epochs=50, batch_size=1, verbose=2)

    # Save model here if needed
    return {"message": "Autoencoder trained successfully"}

# @app.get("/detect_anomalies_autoencoder/{user_id}")
# async def detect_anomalies_autoencoder(user_id: str):
#     df = await fetch_expense_data(user_id)
#     if df.empty:
#         return {"message": "No data available for anomaly detection"}
#
#     df['date'] = pd.to_datetime(df['date'])
#     df.set_index('date', inplace=True)
#     df = df.resample('M').sum()
#
#     # Load a pre-trained autoencoder here
#     model = tf.keras.models.load_model('autoencoder_model.h5')  # Modify path as needed
#     scaler = MinMaxScaler()
#     scaled_data = scaler.fit_transform(df[['amount']])
#     predictions = model.predict(scaled_data)
#     mse = np.mean(np.power(scaled_data - predictions, 2), axis=1)
#     anomaly_threshold = np.percentile(mse, 95)
#     df['anomaly'] = mse > anomaly_threshold
#
#     anomalies = df[df['anomaly']]
#     return {"anomalies": anomalies.to_dict(orient='records')}
#
# @app.get("/cluster_expenses/{user_id}")
# async def cluster_expenses(user_id: str, n_clusters: int = 3):
#     expenses = await fetch_expense_data(user_id)
#     df = pd.DataFrame(expenses)
#     if df.empty or 'description' not in df.columns:
#         return {"message": "No descriptions available for clustering"}
#
#     tfidf = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = tfidf.fit_transform(df['description'])
#     lda = LatentDirichletAllocation(n_components=n_clusters, random_state=42)
#     lda_matrix = lda.fit_transform(tfidf_matrix)
#     kmeans = KMeans(n_clusters=n_clusters)
#     clusters = kmeans.fit_predict(lda_matrix)
#
#     df['cluster'] = clusters
#     return {"clusters": df[['description', 'cluster']].to_dict(orient='records')}