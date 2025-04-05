import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Load the dataset
df = pd.read_csv("data/gas_fees.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["timestamp"] = df["timestamp"].astype("int64") / 10**9  # convert to UNIX time


# Features (X) and Target (y)
X = df[["timestamp", "block_number"]]
y = df["base_fee_gwei"]

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print(f"✅ Model trained!")
print(f"📉 Mean Absolute Error: {mae:.2f} GWEI")

# Save model for future use
import joblib
joblib.dump(model, "models/gas_fee_model.pkl")
