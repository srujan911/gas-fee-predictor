import pandas as pd
from web3 import Web3
import time
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime

load_dotenv()

ETH_NODE = os.getenv("ETHEREUM_NODE_URL")
web3 = Web3(Web3.HTTPProvider(ETH_NODE or "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"))

def collect_block_data(n=10):
    if not web3.is_connected():
        print("❌ Not connected to Ethereum")
        return

    latest_block = web3.eth.block_number
    data = []

    for i in range(latest_block - n, latest_block):
        try:
            block = web3.eth.get_block(i, full_transactions=True)
            timestamp_utc = datetime.utcfromtimestamp(block.timestamp).replace(tzinfo=pytz.utc)
            timestamp_ist = timestamp_utc.astimezone(pytz.timezone("Asia/Kolkata"))

            data.append({
                "block_number": block.number,
                "timestamp": timestamp_utc.isoformat(),
                "timestamp_ist": timestamp_ist.isoformat(),
                "base_fee_gwei": float(block.baseFeePerGas) / 1e9,
                "gas_used": block.gasUsed,
                "gas_limit": block.gasLimit,
                "tx_count": len(block.transactions),
            })

            print(f"✅ Collected block {i}")
            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error at block {i}: {e}")

    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    try:
        df.to_csv("data/gas_fees.csv", index=False, encoding="utf-8")
        print("✅ Data saved to data/gas_fees.csv")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

    print("🔗 Chain ID:", web3.eth.chain_id)

if __name__ == "__main__":
    collect_block_data()
