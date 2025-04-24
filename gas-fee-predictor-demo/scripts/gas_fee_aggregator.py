#!/usr/bin/env python3
"""
Ethereum Gas Fee Aggregator

This script fetches gas fee data from multiple sources and aggregates them
to provide the most accurate gas fee information.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import requests
import json
import time
import logging
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# API Keys (replace with your own if you have them)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YourApiKeyToken")
ETHGASSTATION_API_KEY = os.getenv("ETHGASSTATION_API_KEY", "")
GASNOW_API_KEY = os.getenv("GASNOW_API_KEY", "")

# Cache for gas fee data
gas_fee_cache = {}
gas_fee_cache_timestamp = 0
gas_fee_cache_ttl = 15  # 15 seconds TTL for gas fee data

def connect_to_ethereum():
    """Connect to the Ethereum network using multiple providers."""
    try:
        load_dotenv()
        # Try multiple Ethereum node providers to ensure we get a connection
        providers = [
            os.getenv("ETHEREUM_NODE_URL", "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"),
            "https://eth-mainnet.g.alchemy.com/v2/demo",  # Alchemy demo key
            "https://rpc.ankr.com/eth",  # Ankr public endpoint
            "https://ethereum.publicnode.com"  # Public node
        ]
        
        # Try each provider until we get a connection
        for provider_url in providers:
            logger.info(f"Attempting to connect to Ethereum node: {provider_url}")
            # Set a longer timeout for the HTTP provider (15 seconds)
            web3 = Web3(Web3.HTTPProvider(provider_url, request_kwargs={'timeout': 15}))
            
            try:
                # Test connection with timeout
                if web3.is_connected():
                    # Verify we can get chain ID
                    chain_id = web3.eth.chain_id
                    logger.info(f"Successfully connected to Ethereum network. Chain ID: {chain_id}")
                    return web3
                else:
                    logger.warning(f"Failed to connect to {provider_url}. Trying next provider.")
            except Exception as e:
                logger.warning(f"Error connecting to {provider_url}: {e}. Trying next provider.")
        
        # If we get here, all providers failed
        raise ConnectionError("Failed to connect to any Ethereum node. Please check your internet connection.")
    except Exception as e:
        logger.error(f"Error connecting to Ethereum: {e}")
        raise

def fetch_from_etherscan():
    """Fetch gas fee data from Etherscan Gas Oracle API."""
    try:
        url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data["status"] == "1":
            return {
                "source": "etherscan",
                "timestamp": datetime.now().timestamp(),
                "safe_gas_price": float(data["result"]["SafeGasPrice"]),
                "propose_gas_price": float(data["result"]["ProposeGasPrice"]),
                "fast_gas_price": float(data["result"]["FastGasPrice"]),
                "base_fee": float(data["result"]["suggestBaseFee"])
            }
        else:
            logger.error(f"Etherscan API error: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        logger.error(f"Error fetching from Etherscan: {e}")
        return None

def fetch_from_ethgasstation():
    """Fetch gas fee data from ETH Gas Station API."""
    try:
        api_key_param = f"?api-key={ETHGASSTATION_API_KEY}" if ETHGASSTATION_API_KEY else ""
        url = f"https://ethgasstation.info/api/ethgasAPI.json{api_key_param}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # ETH Gas Station returns prices in tenths of Gwei
        return {
            "source": "ethgasstation",
            "timestamp": datetime.now().timestamp(),
            "safe_gas_price": float(data["safeLow"]) / 10,
            "propose_gas_price": float(data["average"]) / 10,
            "fast_gas_price": float(data["fast"]) / 10,
            "base_fee": float(data.get("baseFee", data["average"])) / 10
        }
    except Exception as e:
        logger.error(f"Error fetching from ETH Gas Station: {e}")
        return None

def fetch_from_blocknative():
    """Fetch gas fee data from Blocknative API."""
    try:
        url = "https://api.blocknative.com/gasprices/blockprices"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Extract the base fee and priority fees
        base_fee = float(data["blockPrices"][0]["baseFeePerGas"]) / 1e9  # Convert to Gwei
        priority_fees = data["blockPrices"][0]["estimatedPrices"]
        
        return {
            "source": "blocknative",
            "timestamp": datetime.now().timestamp(),
            "safe_gas_price": base_fee + float(priority_fees[2]["maxPriorityFeePerGas"]),
            "propose_gas_price": base_fee + float(priority_fees[1]["maxPriorityFeePerGas"]),
            "fast_gas_price": base_fee + float(priority_fees[0]["maxPriorityFeePerGas"]),
            "base_fee": base_fee
        }
    except Exception as e:
        logger.error(f"Error fetching from Blocknative: {e}")
        return None

def fetch_from_web3(web3=None):
    """Fetch gas fee data directly from Ethereum node using Web3."""
    try:
        if web3 is None:
            web3 = connect_to_ethereum()
            
        if not web3:
            logger.error("Failed to connect to Ethereum network")
            return None
            
        # Get latest block
        latest_block = web3.eth.get_block('latest')
        
        # Get base fee per gas (EIP-1559)
        base_fee_wei = latest_block.get("baseFeePerGas", 0)
        base_fee_gwei = float(base_fee_wei) / 1e9
        
        # Get gas price (legacy)
        gas_price_wei = web3.eth.gas_price
        gas_price_gwei = float(gas_price_wei) / 1e9
        
        # For Web3, we use the base fee as the safe price and add priority fees for faster transactions
        return {
            "source": "web3",
            "timestamp": datetime.now().timestamp(),
            "block_number": latest_block.number,
            "safe_gas_price": base_fee_gwei * 1.1,  # Base fee + 10% priority fee
            "propose_gas_price": base_fee_gwei * 1.3,  # Base fee + 30% priority fee
            "fast_gas_price": base_fee_gwei * 1.5,  # Base fee + 50% priority fee
            "base_fee": base_fee_gwei,
            "gas_price": gas_price_gwei
        }
    except Exception as e:
        logger.error(f"Error fetching from Web3: {e}")
        return None

def get_aggregated_gas_fee(web3=None, force_refresh=False):
    """
    Get aggregated gas fee data from multiple sources.
    
    Args:
        web3: Web3 instance (optional)
        force_refresh: Force refresh the cache
        
    Returns:
        dict: Aggregated gas fee data
    """
    global gas_fee_cache, gas_fee_cache_timestamp, gas_fee_cache_ttl
    
    # Check if we have fresh cached data
    current_time = time.time()
    if not force_refresh and gas_fee_cache and (current_time - gas_fee_cache_timestamp) < gas_fee_cache_ttl:
        logger.info("Using cached gas fee data")
        return gas_fee_cache
    
    # Fetch data from multiple sources
    sources = []
    
    # Web3 (direct from Ethereum node)
    web3_data = fetch_from_web3(web3)
    if web3_data:
        sources.append(web3_data)
    
    # Etherscan
    etherscan_data = fetch_from_etherscan()
    if etherscan_data:
        sources.append(etherscan_data)
    
    # ETH Gas Station
    ethgasstation_data = fetch_from_ethgasstation()
    if ethgasstation_data:
        sources.append(ethgasstation_data)
    
    # Blocknative
    blocknative_data = fetch_from_blocknative()
    if blocknative_data:
        sources.append(blocknative_data)
    
    # If we have no data from any source, return None
    if not sources:
        logger.error("Failed to fetch gas fee data from any source")
        return None
    
    # Aggregate the data
    # We prioritize Web3 data for the block number and timestamp
    # For gas prices, we take the median of all sources to avoid outliers
    block_number = None
    block_timestamp = None
    base_fees = []
    safe_gas_prices = []
    propose_gas_prices = []
    fast_gas_prices = []
    
    for source in sources:
        if source["source"] == "web3":
            block_number = source.get("block_number")
            block_timestamp = source.get("timestamp")
        
        base_fees.append(source.get("base_fee", 0))
        safe_gas_prices.append(source.get("safe_gas_price", 0))
        propose_gas_prices.append(source.get("propose_gas_price", 0))
        fast_gas_prices.append(source.get("fast_gas_price", 0))
    
    # Sort and take median
    base_fees.sort()
    safe_gas_prices.sort()
    propose_gas_prices.sort()
    fast_gas_prices.sort()
    
    median_index = len(sources) // 2
    
    # If we have an even number of sources, take the average of the middle two
    if len(sources) % 2 == 0 and len(sources) > 1:
        base_fee = (base_fees[median_index - 1] + base_fees[median_index]) / 2
        safe_gas_price = (safe_gas_prices[median_index - 1] + safe_gas_prices[median_index]) / 2
        propose_gas_price = (propose_gas_prices[median_index - 1] + propose_gas_prices[median_index]) / 2
        fast_gas_price = (fast_gas_prices[median_index - 1] + fast_gas_prices[median_index]) / 2
    else:
        base_fee = base_fees[median_index]
        safe_gas_price = safe_gas_prices[median_index]
        propose_gas_price = propose_gas_prices[median_index]
        fast_gas_price = fast_gas_prices[median_index]
    
    # Create the aggregated data
    aggregated_data = {
        "timestamp": block_timestamp or current_time,
        "block_number": block_number,
        "base_fee_gwei": round(base_fee, 5),
        "safe_gas_price": round(safe_gas_price, 5),
        "propose_gas_price": round(propose_gas_price, 5),
        "fast_gas_price": round(fast_gas_price, 5),
        "sources": [s["source"] for s in sources],
        "source_count": len(sources)
    }
    
    # Update cache
    gas_fee_cache = aggregated_data
    gas_fee_cache_timestamp = current_time
    
    logger.info(f"Aggregated gas fee data from {len(sources)} sources: {aggregated_data['base_fee_gwei']:.5f} Gwei")
    return aggregated_data

def main():
    """Main function to test the gas fee aggregator."""
    try:
        # Get aggregated gas fee data
        gas_fee_data = get_aggregated_gas_fee(force_refresh=True)
        
        if gas_fee_data:
            print("\n" + "=" * 60)
            print("🔮 ETHEREUM GAS FEE AGGREGATOR 🔮")
            print("=" * 60)
            print(f"Block Number: {gas_fee_data.get('block_number', 'N/A')}")
            print(f"Base Fee: {gas_fee_data['base_fee_gwei']:.5f} Gwei")
            print(f"Safe Gas Price: {gas_fee_data['safe_gas_price']:.5f} Gwei")
            print(f"Standard Gas Price: {gas_fee_data['propose_gas_price']:.5f} Gwei")
            print(f"Fast Gas Price: {gas_fee_data['fast_gas_price']:.5f} Gwei")
            print(f"Sources: {', '.join(gas_fee_data['sources'])}")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("❌ ETHEREUM GAS FEE AGGREGATOR ❌")
            print("=" * 60)
            print("Failed to fetch gas fee data from any source.")
            print("=" * 60)
            return 1
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
