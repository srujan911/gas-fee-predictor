import pandas as pd
import joblib
import os


model_path = "models/gas_fee_model.pkl"
if not os.path.exists(model_path):
    print("❌ Trained model not found!")
    exit()

model, scaler = joblib.load(model_path)
df = pd.read_csv("data/gas_fees_cleaned.csv")
features = ["timestamp", "block_number", "gas_used", "gas_limit", "tx_count"]
df = df.dropna(subset=features)
X = df[["timestamp", "block_number", "gas_used", "gas_limit", "tx_count"]].copy()
X["timestamp"] = pd.to_datetime(X["timestamp"], utc=True).astype(int) // 10**9
X_scaled = scaler.transform(X)
df["predicted_fee"] = model.predict(X_scaled)
df["predicted_fee"] = df["predicted_fee"].clip(lower=0)
output_path = "data/gas_fees_with_predictions.csv"
df.to_csv(output_path, index=False)
print(f"✅ Saved with predictions to {output_path}")
