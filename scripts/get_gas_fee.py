from web3 import Web3

# Ethereum node URL (use your Infura URL here)
ETHEREUM_NODE_URL = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"

# Connect to Web3
web3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))

# Check connection
if not web3.is_connected():
    print("❌ Failed to connect")
    exit()

# Fetch latest block
latest_block = web3.eth.get_block('latest')

# Show base fee per gas (EIP-1559 block)
base_fee = latest_block.get('baseFeePerGas', 0)
base_fee_gwei = web3.from_wei(base_fee, 'gwei')

print("✅ Latest Block:", latest_block['number'])
print("📊 Base Fee Per Gas:", base_fee_gwei, "GWEI")
