import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv("data/gas_fees_cleaned.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])
df["timestamp"] = df["timestamp"].astype("int64") // 10**9


X = df[["timestamp", "block_number"]]
y = df["base_fee_gwei"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print("✅ Model trained!")
print(f"📊 Mean Absolute Error: {mae:.2f} GWEI")
joblib.dump((model, scaler), "models/gas_fee_model.pkl")

