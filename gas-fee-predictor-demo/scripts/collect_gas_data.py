#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Data Collection Script

This script connects to the Ethereum blockchain via Infura and collects gas fee data
from recent blocks. It retrieves block information including timestamps, gas usage,
and transaction counts, then saves the data to a CSV file for further processing.

Author: SRUJANJAINI
Date: April 2025
"""

import pandas as pd
from web3 import Web3
import time
import os
import argparse
from dotenv import load_dotenv
import pytz
from datetime import datetime, timezone
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("data_collection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def connect_to_ethereum():
    """Connect to the Ethereum network using Infura."""
    try:
        # Load environment variables
        load_dotenv()
        eth_node = os.getenv("ETHEREUM_NODE_URL")

        if not eth_node:
            eth_node = "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b"
            logger.warning("ETHEREUM_NODE_URL not found in .env file, using default Infura URL")

        logger.info(f"Connecting to Ethereum node")
        web3 = Web3(Web3.HTTPProvider(eth_node))

        if not web3.is_connected():
            logger.error("Failed to connect to Ethereum")
            raise ConnectionError("Not connected to Ethereum")

        chain_id = web3.eth.chain_id
        logger.info(f"Connected to Ethereum network. Chain ID: {chain_id}")
        return web3
    except Exception as e:
        logger.error(f"Error connecting to Ethereum: {e}")
        raise

def collect_block_data(web3, n=100, delay=1.0, output_path="data/gas_fees.csv", tz_name="UTC"):
    """Collect data from the n most recent Ethereum blocks.

    Args:
        web3: Web3 instance connected to Ethereum
        n: Number of blocks to collect (default: 100)
        delay: Delay between requests in seconds (default: 1.0)
        output_path: Path to save the collected data (default: data/gas_fees.csv)
        tz_name: Timezone name for timestamp conversion (default: UTC)
    """
    try:
        logger.info(f"Starting collection of {n} blocks with {delay}s delay")

        # Get latest block number
        latest_block = web3.eth.block_number
        logger.info(f"Latest block number: {latest_block}")

        # Initialize data list
        data = []
        successful_blocks = 0
        failed_blocks = 0

        # Create progress tracking variables
        start_time = time.time()

        # Collect data from blocks
        for i in range(latest_block - n, latest_block):
            try:
                # Get block data
                block = web3.eth.get_block(i, full_transactions=True)

                # Convert timestamp to datetime with timezone
                timestamp_utc = datetime.fromtimestamp(block.timestamp, tz=timezone.utc)

                # Convert to specified timezone
                if tz_name.upper() != "UTC":
                    timestamp_local = timestamp_utc.astimezone(pytz.timezone(tz_name))
                else:
                    timestamp_local = timestamp_utc

                # Extract block data
                block_data = {
                    "block_number": int(block.number),  # Ensure block number is an integer
                    "timestamp": timestamp_utc.isoformat(),
                    f"timestamp_{tz_name.lower()}": timestamp_local.isoformat(),
                    "base_fee_gwei": float(block.baseFeePerGas) / 1e9 if hasattr(block, 'baseFeePerGas') else None,
                    "gas_used": int(block.gasUsed),  # Ensure gas_used is an integer
                    "gas_limit": int(block.gasLimit),  # Ensure gas_limit is an integer
                    "tx_count": len(block.transactions),
                    "gas_used_ratio": float(block.gasUsed) / float(block.gasLimit),  # Calculate ratio from integers
                }

                # Add transaction type counts if available
                tx_types = {0: 0, 1: 0, 2: 0}  # Legacy, EIP-2930, EIP-1559
                for tx in block.transactions:
                    tx_type = tx.get('type', 0)
                    tx_types[tx_type] = tx_types.get(tx_type, 0) + 1

                block_data.update({
                    "legacy_tx_count": tx_types.get(0, 0),
                    "eip2930_tx_count": tx_types.get(1, 0),
                    "eip1559_tx_count": tx_types.get(2, 0),
                })

                # Append to data list
                data.append(block_data)
                successful_blocks += 1

                # Log progress
                if i % 10 == 0 or i == latest_block - 1:
                    elapsed = time.time() - start_time
                    blocks_per_second = successful_blocks / max(elapsed, 0.1)
                    remaining = (latest_block - i - 1) / max(blocks_per_second, 0.1)
                    logger.info(f"Block {i} ({successful_blocks}/{n}): {blocks_per_second:.2f} blocks/s, ~{remaining:.1f}s remaining")
                else:
                    logger.debug(f"Collected block {i}")

                # Delay to avoid rate limiting
                time.sleep(delay)

            except Exception as e:
                logger.warning(f"Error at block {i}: {e}")
                failed_blocks += 1

        # Create DataFrame from collected data
        df = pd.DataFrame(data)

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save data to CSV
        try:
            df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise

        # Log collection summary
        total_time = time.time() - start_time
        logger.info(f"Collection completed in {total_time:.2f} seconds")
        logger.info(f"Successful blocks: {successful_blocks}, Failed blocks: {failed_blocks}")
        logger.info(f"Average collection rate: {successful_blocks / max(total_time, 0.1):.2f} blocks/s")

        # Print summary for user
        print("\n" + "=" * 50)
        print("🔮 ETHEREUM GAS FEE DATA COLLECTION 🔮")
        print("=" * 50)
        print(f"✅ Successfully collected {successful_blocks} blocks")
        print(f"⚠️ Failed to collect {failed_blocks} blocks")
        print(f"💾 Data saved to {output_path}")
        print(f"🕒 Collection time: {total_time:.2f} seconds")
        print(f"🔗 Chain ID: {web3.eth.chain_id}")
        print("=" * 50)

        return df
    except Exception as e:
        logger.error(f"Error in data collection: {e}")
        raise

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Collect Ethereum gas fee data")
    parser.add_argument("-n", "--num-blocks", type=int, default=100,
                        help="Number of blocks to collect (default: 100)")
    parser.add_argument("-d", "--delay", type=float, default=1.0,
                        help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("-o", "--output", type=str, default="data/gas_fees.csv",
                        help="Output file path (default: data/gas_fees.csv)")
    parser.add_argument("-t", "--timezone", type=str, default="UTC",
                        help="Timezone name for timestamp conversion (default: UTC)")
    return parser.parse_args()

def main():
    """Main function to run the data collection."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Connect to Ethereum
        web3 = connect_to_ethereum()

        # Collect block data
        collect_block_data(
            web3,
            n=args.num_blocks,
            delay=args.delay,
            output_path=args.output,
            tz_name=args.timezone
        )

        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
