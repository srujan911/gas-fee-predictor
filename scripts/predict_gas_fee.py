import joblib
import time
from datetime import datetime
from web3 import Web3

# Load trained model
model = joblib.load("models/gas_fee_model.pkl")

# Connect to Ethereum node
ETHEREUM_NODE_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

if not web3.is_connected():
    print("❌ Not connected to Ethereum")
    exit()

# Get current block data
block = web3.eth.get_block("latest")
timestamp = int(time.time())
block_number = block["number"]
baseFeePerGas = block["baseFeePerGas"]
gasUsed = block["gasUsed"]
# gasLimit = block["gasLimit"]  ← Not needed if model was trained on 2 features

# Predict using only 2 features
predicted_fee = model.predict([[baseFeePerGas, gasUsed]])[0]
predicted_fee = max(predicted_fee, 0)  # Clamp to 0 if negative

# Display result
print(f"🧱 Block Number: {block_number}")
print(f"🕒 Timestamp: {datetime.fromtimestamp(timestamp)}")
print(f"🔮 Predicted Base Fee: {predicted_fee:.2f} GWEI")
