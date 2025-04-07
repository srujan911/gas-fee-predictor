import joblib
import time
from datetime import datetime
from web3 import Web3
import pandas as pd


model = joblib.load("models/gas_fee_model.pkl")
ETHEREUM_NODE_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

if not web3.is_connected():
    print("❌ Not connected to Ethereum")
    exit()

block = web3.eth.get_block("latest")
timestamp = time.time()  
block_number = block["number"]

model, scaler = joblib.load("models/gas_fee_model.pkl")

X_new = pd.DataFrame([[timestamp, block_number]], columns=["timestamp", "block_number"])
X_scaled = scaler.transform(X_new)

predicted_fee = model.predict(X_scaled)[0]

print("🧠 Raw Predicted Fee:", predicted_fee)
predicted_fee = max(predicted_fee, 0) 

print(f"📦 Block Number: {block_number}")
print(f"🕒 Timestamp: {datetime.fromtimestamp(timestamp)}")
print(f"⛽ Predicted Base Fee: {predicted_fee:.2f} GWEI")
