
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
        n: Number of blocks to collect (default: 1000)
        delay: Delay between requests in seconds (default: 1.0)
        output_path: Path to save the collected data (default: data/gas_fees.csv)
        tz_name: Timezone name for timestamp conversion (default: UTC)
    """
    try:
        logger.info(f"Starting collection of {n} blocks with {delay}s delay")
        latest_block = web3.eth.block_number
        logger.info(f"Latest block number: {latest_block}")
        data = []
        successful_blocks = 0
        failed_blocks = 0
        start_time = time.time()
        for i in range(latest_block - n, latest_block):
            try:
            
                block = web3.eth.get_block(i, full_transactions=True)
                timestamp_utc = datetime.fromtimestamp(block.timestamp, tz=timezone.utc)
                if tz_name.upper() != "UTC":
                    timestamp_local = timestamp_utc.astimezone(pytz.timezone(tz_name))
                else:
                    timestamp_local = timestamp_utc

                block_data = {
                    "block_number": int(block.number),  
                    "timestamp": timestamp_utc.isoformat(),
                    f"timestamp_{tz_name.lower()}": timestamp_local.isoformat(),
                    "base_fee_gwei": float(block.baseFeePerGas) / 1e9 if hasattr(block, 'baseFeePerGas') else None,
                    "gas_used": int(block.gasUsed),  
                    "gas_limit": int(block.gasLimit),  
                    "tx_count": len(block.transactions),
                    "gas_used_ratio": float(block.gasUsed) / float(block.gasLimit),  
                }

                tx_types = {0: 0, 1: 0, 2: 0}  
                for tx in block.transactions:
                    tx_type = tx.get('type', 0)
                    tx_types[tx_type] = tx_types.get(tx_type, 0) + 1

                block_data.update({
                    "legacy_tx_count": tx_types.get(0, 0),
                    "eip2930_tx_count": tx_types.get(1, 0),
                    "eip1559_tx_count": tx_types.get(2, 0),
                })

        
                data.append(block_data)
                successful_blocks += 1
                if i % 10 == 0 or i == latest_block - 1:
                    elapsed = time.time() - start_time
                    blocks_per_second = successful_blocks / max(elapsed, 0.1)
                    remaining = (latest_block - i - 1) / max(blocks_per_second, 0.1)
                    logger.info(f"Block {i} ({successful_blocks}/{n}): {blocks_per_second:.2f} blocks/s, ~{remaining:.1f}s remaining")
                else:
                    logger.debug(f"Collected block {i}")

                time.sleep(delay)

            except Exception as e:
                logger.warning(f"Error at block {i}: {e}")
                failed_blocks += 1
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise

    
        total_time = time.time() - start_time
        logger.info(f"Collection completed in {total_time:.2f} seconds")
        logger.info(f"Successful blocks: {successful_blocks}, Failed blocks: {failed_blocks}")
        logger.info(f"Average collection rate: {successful_blocks / max(total_time, 0.1):.2f} blocks/s")
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
    parser.add_argument("-n", "--num-blocks", type=int, default=1000,
                        help="Number of blocks to collect (default: 1000)")
    parser.add_argument("-d", "--delay", type=float, default=1.0,
                        help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("-o", "--output", type=str, default="data/gas_fees.csv",
                        help="Output file path (default: data/gas_fees.csv)")
    parser.add_argument("-t", "--timezone", type=str, default="UTC",
                        help="Timezone name for timestamp conversion (default: UTC)")
    return parser.parse_args()

def collect_ethereum_gas_data(num_blocks=1000, timezone="UTC"):
    """Function to collect Ethereum gas data for the pipeline."""
    try:
        logger.info(f"Collecting {num_blocks} blocks of Ethereum gas data with timezone {timezone}")
        web3 = connect_to_ethereum()
        collect_block_data(
            web3,
            n=num_blocks,
            delay=0.5,  
            output_path="data/gas_fees.csv",
            tz_name=timezone
        )

        logger.info("Gas data collection completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error collecting Ethereum gas data: {e}")
        return False

def main():
    """Main function to run the data collection."""
    try:
        args = parse_arguments()
        web3 = connect_to_ethereum()
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
