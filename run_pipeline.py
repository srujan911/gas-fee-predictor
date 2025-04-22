#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Pipeline Runner

This script runs the complete gas fee prediction pipeline:
1. Collect data from Ethereum blockchain
2. Clean and preprocess the data
3. Train the prediction model
4. Make predictions and visualize results

Author: SRUJANJAINI
Date: April 2025
"""

import os
import argparse
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Ethereum gas fee prediction pipeline")
    parser.add_argument("-n", "--num-blocks", type=int, default=100,
                        help="Number of blocks to collect (default: 100)")
    parser.add_argument("-c", "--collect-only", action="store_true",
                        help="Only collect data, don't train model")
    parser.add_argument("-t", "--train-only", action="store_true",
                        help="Only train model, don't collect data")
    parser.add_argument("-v", "--visualize", action="store_true",
                        help="Generate visualizations")
    parser.add_argument("-p", "--predict", action="store_true",
                        help="Make a prediction after training")
    parser.add_argument("-i", "--improved", action="store_true",
                        help="Use improved gas fee prediction")
    parser.add_argument("--timezone", type=str, default="UTC",
                        help="Timezone for timestamp conversion (default: UTC)")
    return parser.parse_args()

def run_data_collection(num_blocks, timezone):
    """Run the data collection step."""
    logger.info("Starting data collection step")
    start_time = time.time()

    try:
        from scripts.collect_gas_data import connect_to_ethereum, collect_block_data

        # Connect to Ethereum
        web3 = connect_to_ethereum()

        # Collect block data
        collect_block_data(
            web3,
            n=num_blocks,
            delay=1.0,
            output_path="data/gas_fees.csv",
            tz_name=timezone
        )

        elapsed = time.time() - start_time
        logger.info(f"Data collection completed in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error in data collection: {e}")
        return False

def run_data_cleaning():
    """Run the data cleaning step."""
    logger.info("Starting data cleaning step")
    start_time = time.time()

    try:
        from scripts.clean_data import clean_gas_data

        # Clean the data
        cleaned_data = clean_gas_data(
            input_path="data/gas_fees.csv",
            output_path="data/gas_fees_cleaned.csv"
        )

        if cleaned_data is None or cleaned_data.empty:
            logger.error("Data cleaning failed or resulted in empty dataset")
            return False

        elapsed = time.time() - start_time
        logger.info(f"Data cleaning completed in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error in data cleaning: {e}")
        return False

def run_model_training():
    """Run the model training step."""
    logger.info("Starting model training step")
    start_time = time.time()

    try:
        # Import here to avoid loading unnecessary modules
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from scripts.train_model import main as train_main

        # Train the model
        result = train_main()

        if result != 0:
            logger.error("Model training failed")
            return False

        elapsed = time.time() - start_time
        logger.info(f"Model training completed in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        return False

def run_prediction(use_improved=False):
    """Run the prediction step."""
    logger.info("Starting prediction step")
    start_time = time.time()

    try:
        # Import here to avoid loading unnecessary modules
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        if use_improved:
            logger.info("Using improved prediction model")
            from scripts.improved_gas_fee import main as predict_main
        else:
            from scripts.get_gas_fee_new import main as predict_main

        # Make prediction
        result = predict_main()

        if result != 0:
            logger.error("Prediction failed")
            return False

        elapsed = time.time() - start_time
        logger.info(f"Prediction completed in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return False

def run_visualization():
    """Run the visualization step."""
    logger.info("Starting visualization step")
    start_time = time.time()

    try:
        # Add predictions to CSV
        from scripts.add_predictions_to_csv import main as add_predictions_main
        add_predictions_main()

        # Generate visualizations
        logger.info("Generating visualizations")

        # Import visualization modules
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend

        # Create visualizations directory
        os.makedirs("visualizations", exist_ok=True)

        # Run visualization scripts
        from scripts.visualize_gas_fees import main as visualize_fees_main
        from scripts.visualize_comparison import main as visualize_comparison_main

        visualize_fees_main(save_path="visualizations/gas_fees.png")
        visualize_comparison_main(save_path="visualizations/comparison.png")

        elapsed = time.time() - start_time
        logger.info(f"Visualization completed in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error in visualization: {e}")
        return False

def main():
    """Main function to run the pipeline."""
    # Parse command line arguments
    args = parse_arguments()

    # Print banner
    print("\n" + "=" * 60)
    print("🔮 ETHEREUM GAS FEE PREDICTION PIPELINE 🔮")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # Track overall pipeline success
    pipeline_success = True
    start_time = time.time()

    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # Run pipeline steps based on arguments
    if not args.train_only:
        # Data collection
        print("\n📡 STEP 1: DATA COLLECTION")
        collection_success = run_data_collection(args.num_blocks, args.timezone)
        pipeline_success = pipeline_success and collection_success

        if not collection_success:
            print("❌ Data collection failed. Check logs for details.")
            if not os.path.exists("data/gas_fees.csv"):
                print("❌ Cannot proceed without data. Pipeline terminated.")
                return 1
            print("⚠️ Using existing data to continue pipeline.")

        # Data cleaning
        print("\n🧹 STEP 2: DATA CLEANING")
        cleaning_success = run_data_cleaning()
        pipeline_success = pipeline_success and cleaning_success

        if not cleaning_success:
            print("❌ Data cleaning failed. Check logs for details.")
            if not os.path.exists("data/gas_fees_cleaned.csv"):
                print("❌ Cannot proceed without cleaned data. Pipeline terminated.")
                return 1
            print("⚠️ Using existing cleaned data to continue pipeline.")

    if not args.collect_only:
        # Model training
        print("\n🧠 STEP 3: MODEL TRAINING")
        training_success = run_model_training()
        pipeline_success = pipeline_success and training_success

        if not training_success:
            print("❌ Model training failed. Check logs for details.")
            if not os.path.exists("models/gas_fee_model.pkl"):
                print("❌ Cannot proceed without trained model. Pipeline terminated.")
                return 1
            print("⚠️ Using existing model to continue pipeline.")

        # Prediction
        if args.predict:
            print("\n🔮 STEP 4: PREDICTION")
            if args.improved:
                print("Using improved prediction model")
            prediction_success = run_prediction(use_improved=args.improved)
            pipeline_success = pipeline_success and prediction_success

            if not prediction_success:
                print("❌ Prediction failed. Check logs for details.")

        # Visualization
        if args.visualize:
            print("\n📊 STEP 5: VISUALIZATION")
            visualization_success = run_visualization()
            pipeline_success = pipeline_success and visualization_success

            if not visualization_success:
                print("❌ Visualization failed. Check logs for details.")

    # Print summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("🏁 PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {elapsed:.2f} seconds")
    print(f"Overall status: {'✅ Success' if pipeline_success else '❌ Failed'}")
    print("=" * 60)

    return 0 if pipeline_success else 1

if __name__ == "__main__":
    exit(main())
