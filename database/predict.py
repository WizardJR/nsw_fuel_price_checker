import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from DatabaseR import DatabaseR
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH", "fuel_prices.db")
DB_PREDICT_PATH = os.getenv("DB_PREDICT_PATH")
FUEL_TYPES = os.getenv("FUEL_TYPES").split(",")
SEQ_LENGTH = int(os.getenv("SEQ_LENGTH"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE"))
EPOCHS = int(os.getenv("EPOCHS"))
PATIENCE = int(os.getenv("PATIENCE"))
MODEL_PATH = os.getenv("MODEL_PATH")
DEVICE_ENV = os.getenv("DEVICE", "cpu")
if DEVICE_ENV == "xpu" and hasattr(torch, "xpu") and torch.xpu.is_available():
    DEVICE = torch.device("xpu")
else:
    DEVICE = torch.device("cpu")

def load_data(db_path, fuel_type):
    db = DatabaseR(db_path)
    df = db.fetch_average_price(fuel_type=fuel_type, interval="D")
    db.unload()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_pivot = df.pivot_table(index="timestamp", columns="station_code", values="price")

    df_pivot.bfill(inplace=True)
    daily_avg = df_pivot.mean(axis=1).to_frame(name="avg_price")
    return daily_avg

def create_sequences(scaled_df, seq_length):
    X, y = [], []
    for i in range(len(scaled_df) - seq_length):
        X.append(scaled_df.iloc[i:i+seq_length].values)
        y.append(scaled_df.iloc[i+seq_length].values[0])
    return np.array(X), np.array(y)

class PriceDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def train_model(train_loader, val_loader, device, model_path, epochs=EPOCHS, patience=PATIENCE):
    model = LSTMModel().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    best_val_loss = float('inf')
    counter = 0

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            output = model(batch_X).squeeze(-1)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                output = model(batch_X).squeeze(-1)
                loss = criterion(output, batch_y)
                val_loss += loss.item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        print(f"Epoch {epoch+1}: Train Loss: {train_loss:.5f}, Val Loss: {val_loss:.5f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            counter = 0
            torch.save(model.state_dict(), model_path)
        else:
            counter += 1
            if counter >= patience:
                print("Early stopping.")
                break
    return model

def forecast_future(model, X, scaler, device, fuel_type, last_date, future_days=30):
    last_seq = torch.tensor(X[-1], dtype=torch.float32).unsqueeze(0).to(device)
    future_preds = []
    model.eval()

    with torch.no_grad():
        for _ in range(future_days):
            output = model(last_seq)
            avg_price = output.mean().item()
            future_preds.append(avg_price)
            next_input = torch.full((1, 1, last_seq.shape[2]), avg_price, dtype=torch.float32).to(device)
            last_seq = torch.cat([last_seq[:, 1:, :], next_input], dim=1)

    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=future_days)
    future_preds_inverse = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1)).flatten()
    
    save_forecast_to_db(DB_PREDICT_PATH, future_dates, future_preds_inverse, fuel_type)
    print(f"Saved {future_days} days of forecast to the database.")
    return future_dates, future_preds_inverse

def save_forecast_to_db(db_path, dates, prices, fuel_type):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS future_forecast (
            id INTEGER PRIMARY KEY,
            timestamp INTEGER NOT NULL,
            forecast_price REAL NOT NULL,
            fuel_type TEXT NOT NULL
        )
    """)

    data = [(int(date.timestamp()), float(price), fuel_type) for date, price in zip(dates, prices)]
    cursor.executemany("INSERT INTO future_forecast (timestamp, forecast_price, fuel_type) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()

def main():
    print(f"Using device: {DEVICE}")
    for fuel_type in FUEL_TYPES:
        print(f"\n=== Processing fuel type: {fuel_type} ===")
        daily_avg = load_data(DB_PATH, fuel_type)

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(daily_avg)
        scaled_df = pd.DataFrame(scaled, index=daily_avg.index, columns=["avg_price"])

        X, y = create_sequences(scaled_df, SEQ_LENGTH)

        print("Final X shape:", X.shape)
        print("Final y shape:", y.shape)

        dataset = PriceDataset(X, y)

        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=False)
        val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

        print("Training model...")
        model = train_model(train_loader, val_loader, DEVICE, MODEL_PATH)
        print("Forecasting future prices...")
        forecast_future(model, X, scaler, DEVICE, fuel_type, daily_avg.index[-1])

if __name__ == "__main__":
    main()