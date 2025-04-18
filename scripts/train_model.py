import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import joblib

df = pd.read_csv("data/gas_fees_cleaned.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])
df["timestamp"] = df["timestamp"].astype("int64") // 10**9
df = df.dropna(subset=["timestamp", "block_number", "gas_used", "gas_limit", "tx_count", "base_fee_gwei"])
X = df[["timestamp", "block_number", "gas_used", "gas_limit", "tx_count"]]
y = df["base_fee_gwei"]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=6)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print("✅ Model trained with XGBoost!")
print(f"📉 Mean Absolute Error: {mae:.2f} GWEI")
joblib.dump((model, scaler), "models/gas_fee_model.pkl")
