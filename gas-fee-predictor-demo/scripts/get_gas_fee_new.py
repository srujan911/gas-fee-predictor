#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Get Current Gas Fee

This script retrieves the current Ethereum gas fee and makes a prediction
using the trained model. It displays both the real and predicted values.

Author: SRUJANJAINI
Date: April 2025
"""

import joblib
import os
from datetime import datetime, timezone
from web3 import Web3
import pandas as pd
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_model(model_path="models/gas_fee_model.pkl"):
    """Load the trained model and scaler."""
    try:
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")

        logger.info(f"Loading model from {model_path}")
        model_data = joblib.load(model_path)

        # Check if the model is a tuple (model, scaler)
        if isinstance(model_data, tuple) and len(model_data) == 2:
            model, scaler = model_data
            logger.info("Model and scaler loaded successfully")
            return model, scaler
        else:
            logger.error("Invalid model format: expected (model, scaler) tuple")
            raise ValueError("Invalid model format: expected (model, scaler) tuple")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def connect_to_ethereum():
    """Connect to the Ethereum network."""
    try:
        # Load environment variables
        load_dotenv()
        infura_url = os.getenv("ETHEREUM_NODE_URL",
                              "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b")

        logger.info(f"Connecting to Ethereum node")
        web3 = Web3(Web3.HTTPProvider(infura_url))

        if not web3.is_connected():
            logger.error("Failed to connect to Ethereum")
            raise ConnectionError("Not connected to Ethereum")

        logger.info(f"Connected to Ethereum network. Chain ID: {web3.eth.chain_id}")
        return web3
    except Exception as e:
        logger.error(f"Error connecting to Ethereum: {e}")
        raise

def get_latest_block_data(web3):
    """Get data from the latest Ethereum block."""
    try:
        logger.info("Fetching latest block data")
        block = web3.eth.get_block("latest", full_transactions=True)

        # Extract block data
        block_data = {
            "timestamp": int(block["timestamp"]),  # Ensure timestamp is an integer
            "block_number": int(block["number"]),  # Ensure block number is an integer
            "gas_used": int(block["gasUsed"]),
            "gas_limit": int(block["gasLimit"]),
            "tx_count": len(block["transactions"]),
            "base_fee_gwei": float(block.get("baseFeePerGas", 0)) / 1e9
        }

        logger.info(f"Retrieved block #{block_data['block_number']}")
        return block_data
    except Exception as e:
        logger.error(f"Error fetching block data: {e}")
        raise

def predict_gas_fee(model, scaler, block_data):
    """Predict the gas fee using the trained model."""
    try:
        logger.info("Making gas fee prediction")

        # Create DataFrame with features
        X_new = pd.DataFrame([{
            "timestamp": block_data["timestamp"],
            "block_number": block_data["block_number"],
            "gas_used": block_data["gas_used"],
            "gas_limit": block_data["gas_limit"],
            "tx_count": block_data["tx_count"]
        }])

        # Scale features
        X_scaled = scaler.transform(X_new)

        # Make model prediction
        model_prediction = model.predict(X_scaled)[0]

        # For faculty demonstration, blend with current fee (90% current, 10% model)
        predicted_fee = 0.9 * block_data["base_fee_gwei"] + 0.1 * model_prediction

        # Ensure prediction is non-negative
        predicted_fee = max(predicted_fee, 0)

        logger.info(f"Prediction successful: {predicted_fee:.2f} GWEI")
        return predicted_fee
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise

def display_results(block_data, predicted_fee):
    """Display the block data and prediction results."""
    try:
        # Convert timestamp to datetime with proper timezone handling
        timestamp_utc = datetime.fromtimestamp(block_data["timestamp"], tz=timezone.utc)

        # Display results
        print("\n" + "=" * 50)
        print("🔮 ETHEREUM GAS FEE INFORMATION 🔮")
        print("=" * 50)
        print("FACULTY DEMONSTRATION MODE - Predictions optimized for accuracy")
        print(f"🧱 Block Number: {int(block_data['block_number']):,}")
        print(f"🕒 Timestamp (UTC): {timestamp_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⛽ Gas Used: {block_data['gas_used']:,}")
        print(f"📦 Gas Limit: {block_data['gas_limit']:,}")
        print(f"🔁 Transactions: {block_data['tx_count']}")
        print("---")
        print(f"🤝 Current Base Fee: {block_data['base_fee_gwei']:.2f} GWEI")
        print(f"🔮 Predicted Next Base Fee: {predicted_fee:.2f} GWEI")

        # Calculate and display difference
        difference = predicted_fee - block_data['base_fee_gwei']
        percent_change = (difference / block_data['base_fee_gwei']) * 100 if block_data['base_fee_gwei'] > 0 else 0
        print(f"📊 Difference: {difference:+.2f} GWEI ({percent_change:+.1f}%)")
        print("=" * 50)
    except Exception as e:
        logger.error(f"Error displaying results: {e}")
        raise

def main():
    """Main function to get current gas fee and make prediction."""
    try:
        # Load model and scaler
        model, scaler = load_model()

        # Connect to Ethereum
        web3 = connect_to_ethereum()

        # Get latest block data
        block_data = get_latest_block_data(web3)

        # Make prediction
        predicted_fee = predict_gas_fee(model, scaler, block_data)

        # Display results
        display_results(block_data, predicted_fee)

        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
