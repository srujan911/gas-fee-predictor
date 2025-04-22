#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Faculty Demonstration Script

This script provides an easy way to run the gas fee prediction pipeline
with a configurable number of blocks for faculty demonstrations.

Author: SRUJANJAINI
Date: April 2025
"""

import argparse
import os
import subprocess
import time
from datetime import datetime

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run gas fee prediction for faculty demonstration")
    parser.add_argument("-n", "--num-blocks", type=int, default=50,
                        help="Number of blocks to collect (default: 50)")
    parser.add_argument("-t", "--timezone", type=str, default="Asia/Kolkata",
                        help="Timezone for visualization (default: Asia/Kolkata)")
    parser.add_argument("-f", "--full", action="store_true",
                        help="Run full pipeline (collect, clean, train, predict, visualize)")
    parser.add_argument("-c", "--collect-only", action="store_true",
                        help="Only collect data, don't train model")
    parser.add_argument("-p", "--predict-only", action="store_true",
                        help="Only make a prediction using existing model")
    parser.add_argument("-i", "--improved", action="store_true",
                        help="Use improved gas fee prediction")
    parser.add_argument("-v", "--visualize-only", action="store_true",
                        help="Only generate visualizations")
    return parser.parse_args()

def run_command(command):
    """Run a command and print its output."""
    print(f"\n> Running: {command}")
    start_time = time.time()
    result = subprocess.run(command, shell=True, text=True)
    elapsed = time.time() - start_time
    print(f"> Command completed in {elapsed:.2f} seconds with exit code {result.returncode}")
    return result.returncode

def main():
    """Main function to run the demonstration."""
    args = parse_arguments()

    # Print banner
    print("\n" + "=" * 60)
    print("🎓 ETHEREUM GAS FEE PREDICTOR - FACULTY DEMONSTRATION 🎓")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Number of blocks: {args.num_blocks}")
    print(f"Timezone: {args.timezone}")
    print("-" * 60)

    # Print explanation about feature importance
    if args.full or not (args.collect_only or args.predict_only or args.visualize_only):
        print("\nNOTE ABOUT FEATURE IMPORTANCE:")
        print("When you see feature importance values (e.g., gas_used: 0.2871), these")
        print("represent the relative importance of each feature in the prediction model,")
        print("NOT the actual values of these features. Values range from 0 to 1, with")
        print("higher values indicating greater importance in making predictions.")
        print("The sum of all importance values equals 1 (or 100%).")
        print("-" * 60)

    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("visualizations", exist_ok=True)

    # Run the appropriate commands based on arguments
    if args.full:
        # Run full pipeline
        print("\n📡 STEP 1: COLLECTING GAS FEE DATA")
        run_command(f"python scripts/collect_gas_data.py -n {args.num_blocks} -t {args.timezone}")

        print("\n🧹 STEP 2: CLEANING DATA")
        run_command("python scripts/clean_data.py")

        print("\n🧠 STEP 3: TRAINING MODEL")
        run_command("python scripts/train_model.py")

        print("\n🔮 STEP 4: MAKING PREDICTION")
        if args.improved:
            print("Using improved prediction model")
            run_command("python scripts/improved_gas_fee.py")
        else:
            run_command("python scripts/get_gas_fee_new.py")

        print("\n📊 STEP 5: GENERATING VISUALIZATIONS")
        run_command("python scripts/add_predictions_to_csv.py")
        run_command(f"python scripts/visualize_gas_fees.py -t {args.timezone} -s visualizations/gas_fees.png")
        run_command(f"python scripts/visualize_comparison.py -t {args.timezone} -s visualizations/comparison.png")

    elif args.collect_only:
        # Only collect data
        print("\n📡 COLLECTING GAS FEE DATA")
        run_command(f"python scripts/collect_gas_data.py -n {args.num_blocks} -t {args.timezone}")

    elif args.predict_only:
        # Only make prediction
        print("\n🔮 MAKING PREDICTION")
        if args.improved:
            print("Using improved prediction model")
            run_command("python scripts/improved_gas_fee.py")
        else:
            run_command("python scripts/get_gas_fee_new.py")

    elif args.visualize_only:
        # Only generate visualizations
        print("\n📊 GENERATING VISUALIZATIONS")
        run_command("python scripts/add_predictions_to_csv.py")
        run_command(f"python scripts/visualize_gas_fees.py -t {args.timezone} -s visualizations/gas_fees.png")
        run_command(f"python scripts/visualize_comparison.py -t {args.timezone} -s visualizations/comparison.png")

    else:
        # Default: collect data and make prediction
        print("\n📡 STEP 1: COLLECTING GAS FEE DATA")
        run_command(f"python scripts/collect_gas_data.py -n {args.num_blocks} -t {args.timezone}")

        print("\n🧹 STEP 2: CLEANING DATA")
        run_command("python scripts/clean_data.py")

        print("\n🔮 STEP 3: MAKING PREDICTION")
        if args.improved:
            print("Using improved prediction model")
            run_command("python scripts/improved_gas_fee.py")
        else:
            run_command("python scripts/get_gas_fee_new.py")

    # Print summary
    print("\n" + "=" * 60)
    print("🎓 DEMONSTRATION COMPLETED 🎓")
    print("=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    exit(main())
