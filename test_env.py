from web3 import Web3

# Directly set the Ethereum Node URL
ETHEREUM_NODE_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"

# Connect to Ethereum node
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

# Check connection
if web3.is_connected():
    print("✅ SUCCESS: Connected to Ethereum!")
    print("Latest block number:", web3.eth.block_number)
else:
    print("❌ ERROR: Connection failed.")
