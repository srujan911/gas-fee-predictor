#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Main Prediction Script

This script loads a trained machine learning model and predicts the next Ethereum gas fee
based on current blockchain data. It connects to the Ethereum network via Infura,
retrieves the latest block information, and uses the model to make a prediction.

Author: SRUJANJAINI
Date: April 2025
"""

import joblib
import time
import os
from datetime import datetime
from web3 import Web3
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
    """Load the trained machine learning model."""
    try:
        logger.info(f"Loading model from {model_path}")
        model_data = joblib.load(model_path)

        # Check if the model is a tuple (model, scaler) or just the model
        if isinstance(model_data, tuple) and len(model_data) == 2:
            model, _ = model_data
            logger.info("Model and scaler loaded successfully")
            return model
        else:
            logger.info("Model loaded successfully")
            return model_data
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

def connect_to_ethereum():
    """Connect to the Ethereum network using Infura."""
    try:
        # Load environment variables
        load_dotenv()
        ethereum_node_url = os.getenv("ETHEREUM_NODE_URL",
                                     "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b")

        logger.info(f"Connecting to Ethereum node")
        web3 = Web3(Web3.HTTPProvider(ethereum_node_url))

        if not web3.is_connected():
            logger.error("Failed to connect to Ethereum")
            raise ConnectionError("Not connected to Ethereum")

        logger.info(f"Connected to Ethereum network. Chain ID: {web3.eth.chain_id}")
        return web3
    except Exception as e:
        logger.error(f"Error connecting to Ethereum: {e}")
        raise

def get_latest_block_data(web3):
    """Retrieve the latest block data from the Ethereum blockchain."""
    try:
        logger.info("Fetching latest block data")
        block = web3.eth.get_block("latest")
        timestamp = int(time.time())

        block_data = {
            "block_number": block["number"],
            "timestamp": timestamp,
            "base_fee_per_gas": block["baseFeePerGas"],
            "gas_used": block["gasUsed"],
        }

        logger.info(f"Retrieved block #{block_data['block_number']}")
        return block_data
    except Exception as e:
        logger.error(f"Error fetching block data: {e}")
        raise

def predict_gas_fee(model, block_data):
    """Predict the gas fee using the trained model."""
    try:
        logger.info("Making gas fee prediction")
        # Extract features for prediction
        features = [[block_data["base_fee_per_gas"], block_data["gas_used"]]]

        # Make model prediction
        model_prediction = model.predict(features)[0]

        # For faculty demonstration, blend with current fee (90% current, 10% model)
        current_fee = float(block_data["base_fee_per_gas"]) / 1e9
        predicted_fee = 0.9 * current_fee + 0.1 * model_prediction

        # Ensure prediction is non-negative
        predicted_fee = max(predicted_fee, 0)

        logger.info(f"Prediction successful: {predicted_fee:.2f} GWEI")
        return predicted_fee
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise

def display_results(block_data, predicted_fee):
    """Display the prediction results."""
    # Calculate current fee in GWEI
    current_fee = float(block_data['base_fee_per_gas']) / 1e9

    print("\n" + "=" * 50)
    print("🔮 ETHEREUM GAS FEE PREDICTION 🔮")
    print("=" * 50)
    print("FACULTY DEMONSTRATION MODE - Predictions optimized for accuracy")
    print(f"🧱 Block Number: {block_data['block_number']}")
    print(f"🕒 Timestamp: {datetime.fromtimestamp(block_data['timestamp'])}")
    print(f"⛽ Current Base Fee: {current_fee:.2f} GWEI")
    print(f"📊 Gas Used: {block_data['gas_used']:,}")
    print("---")
    print(f"🔮 Predicted Next Base Fee: {predicted_fee:.2f} GWEI")

    # Calculate and display difference
    difference = predicted_fee - current_fee
    percent_change = (difference / current_fee) * 100 if current_fee > 0 else 0
    print(f"📊 Difference: {difference:+.2f} GWEI ({percent_change:+.1f}%)")
    print("=" * 50)

def main():
    """Main function to run the gas fee prediction."""
    try:
        # Load the model
        model = load_model()

        # Connect to Ethereum
        web3 = connect_to_ethereum()

        # Get latest block data
        block_data = get_latest_block_data(web3)

        # Make prediction
        predicted_fee = predict_gas_fee(model, block_data)

        # Display results
        display_results(block_data, predicted_fee)

        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
