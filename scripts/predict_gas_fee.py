import joblib
import time
from datetime import datetime
from web3 import Web3
import numpy as np
import pandas as pd

# Load trained model
model = joblib.load("models/gas_fee_model.pkl")

# Connect to Ethereum node
ETHEREUM_NODE_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

if not web3.is_connected():
    print("❌ Not connected to Ethereum")
    exit()

# Get current data
block = web3.eth.get_block("latest")
timestamp = int(time.time())
block_number = block["number"]

# Make prediction
X_new = pd.DataFrame([[timestamp, block_number]], columns=["timestamp", "block_number"])
predicted_gas = model.predict(X_new)[0]

print("📦 Block Number:", block_number)
print("🕒 Timestamp:", datetime.fromtimestamp(timestamp))
print(f"🔮 Predicted Base Fee: {predicted_gas:.2f} GWEI")
