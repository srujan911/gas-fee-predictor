import csv
import time
from datetime import datetime
from web3 import Web3


ETHEREUM_NODE_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

if not web3.is_connected():
    print("❌ Error: Not connected to Ethereum")
    exit()


csv_file = "data/gas_fees.csv"

def create_csv_if_needed():
    try:
        with open(csv_file, "x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "block_number", "base_fee_gwei"])
            print("📄 Created new CSV file.")
    except FileExistsError:
        pass 


def save_gas_data():
    block = web3.eth.get_block("latest")
    base_fee = block.get("baseFeePerGas", 0)
    base_fee_gwei = web3.from_wei(base_fee, "gwei")

    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), block["number"], base_fee_gwei])
        print(f"✅ Saved: Block {block['number']}, Fee {base_fee_gwei:.2f} GWEI")


create_csv_if_needed()


while True:
    save_gas_data()
    time.sleep(15)
