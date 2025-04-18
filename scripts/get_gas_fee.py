import joblib
import os
from datetime import datetime
from web3 import Web3
import pandas as pd

model_path = "models/gas_fee_model.pkl"
if not os.path.exists(model_path):
    print("❌ Trained model not found!")
    exit()

model, scaler = joblib.load(model_path)

INFURA_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not web3.is_connected():
    print("❌ Not connected to Ethereum")
    exit()

block = web3.eth.get_block("latest", full_transactions=True)
timestamp = block["timestamp"]
block_number = block["number"]
gas_used = block["gasUsed"]
gas_limit = block["gasLimit"]
tx_count = len(block["transactions"])
X_new = pd.DataFrame([{
    "timestamp": timestamp,
    "block_number": block_number,
    "gas_used": gas_used,
    "gas_limit": gas_limit,
    "tx_count": tx_count
}])
X_scaled = scaler.transform(X_new)
predicted_fee = model.predict(X_scaled)[0]
predicted_fee = max(predicted_fee, 0)
real_base_fee = block.get("baseFeePerGas", 0) / 1e9  

print(f"🧱 Block Number: {block_number}")
print(f"🕒 Timestamp: {datetime.fromtimestamp(timestamp)}")
print(f"⛽ Gas Used: {gas_used}")
print(f"📦 Gas Limit: {gas_limit}")
print(f"🔁 Transactions: {tx_count}")
print(f"🔮 Predicted Base Fee: {predicted_fee:.2f} GWEI")
print(f"🤝 Real Base Fee: {real_base_fee:.2f} GWEI")
