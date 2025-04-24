#!/usr/bin/env python
"""
Scheduled data collector for Ethereum gas fees.
This script is designed to be run as a scheduled task (e.g., via cron or Windows Task Scheduler)
to collect gas fee data at regular intervals.
"""

import os
import sys
import time
import logging
import pandas as pd
from datetime import datetime
import pytz
from web3 import Web3
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_collector.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("data_collector")

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
project_dir = os.path.dirname(script_dir)
# Add the project directory to the Python path
sys.path.append(project_dir)

# Import project modules
from data.ethereum_data import EthereumDataCollector

def collect_data(num_blocks=10):
    """
    Collect gas fee data from the Ethereum network and append it to the existing dataset.

    Args:
        num_blocks (int): Number of recent blocks to collect data from

    Returns:
        bool: True if data collection was successful, False otherwise
    """
    try:
        logger.info(f"Starting scheduled data collection for {num_blocks} blocks")

        # Initialize the data collector
        collector = EthereumDataCollector()

        # Connect to Ethereum network
        if not collector.connect():
            logger.error("Failed to connect to Ethereum network")
            return False

        logger.info(f"Connected to Ethereum network. Chain ID: {collector.w3.eth.chain_id}")

        # Collect data from recent blocks
        logger.info(f"Fetching data from {num_blocks} recent blocks")
        block_data = collector.collect_block_data(num_blocks)

        if not block_data or len(block_data) == 0:
            logger.error("No data collected")
            return False

        logger.info(f"Retrieved data from {len(block_data)} blocks")

        # Create a DataFrame from the collected data
        df = pd.DataFrame(block_data)

        # Ensure the data directory exists
        data_dir = os.path.join(project_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Path to the data file
        data_file = os.path.join(data_dir, 'gas_fees_cleaned.csv')

        # Check if the file already exists
        if os.path.exists(data_file):
            # Load existing data
            existing_df = pd.read_csv(data_file)
            logger.info(f"Loaded existing data with {len(existing_df)} records")

            # Append new data
            combined_df = pd.concat([existing_df, df], ignore_index=True)

            # Remove duplicates based on block number
            if 'block_number' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['block_number'], keep='last')

            # Sort by timestamp
            if 'timestamp' in combined_df.columns:
                combined_df = combined_df.sort_values('timestamp')

            logger.info(f"Combined data now has {len(combined_df)} records")

            # Save the combined data
            combined_df.to_csv(data_file, index=False)
        else:
            # Save the new data as the first dataset
            df.to_csv(data_file, index=False)
            logger.info(f"Created new data file with {len(df)} records")

        logger.info("Data collection completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error collecting data: {e}")
        return False

def check_and_run_model_fine_tuning():
    """Check if we should run model fine-tuning and run it if needed."""
    try:
        # Import the model fine-tuning module
        from model_fine_tuning import check_data_size, main as fine_tune_models

        # Check if we have enough data for fine-tuning
        if check_data_size():
            logger.info("Running model fine-tuning...")
            result = fine_tune_models()
            if result == 0:
                logger.info("Model fine-tuning completed successfully")
            else:
                logger.error("Model fine-tuning failed")
        else:
            logger.info("Not enough data for model fine-tuning. Skipping.")

    except Exception as e:
        logger.error(f"Error checking/running model fine-tuning: {e}")

def main():
    """Main function to run the scheduled data collection."""
    start_time = time.time()
    success = collect_data(num_blocks=10)  # Collect data from 10 recent blocks
    end_time = time.time()

    if success:
        logger.info(f"Data collection completed in {end_time - start_time:.2f} seconds")

        # Check if we should run model fine-tuning
        # Only run fine-tuning once a day (at midnight)
        current_hour = datetime.now().hour
        if current_hour == 0:
            logger.info("Midnight detected. Checking if model fine-tuning is needed...")
            check_and_run_model_fine_tuning()
    else:
        logger.error("Data collection failed")

    # Generate timestamp for the log
    timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S %Z')
    logger.info(f"Scheduled run completed at {timestamp}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
