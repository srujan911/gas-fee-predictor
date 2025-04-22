#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Comparison Visualization

This script creates a visualization comparing real vs predicted Ethereum gas fees.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pytz
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_data(file_path="data/gas_fees_with_predictions.csv"):
    """Load and preprocess gas fee data with predictions."""
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df = df.dropna(subset=["timestamp", "base_fee_gwei", "predicted_fee"])

        logger.info(f"Loaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def create_comparison_plot(df, timezone="Asia/Kolkata", save_path=None):
    """Create a comparison plot of real vs predicted gas fees."""
    try:
        logger.info(f"Creating comparison plot with timezone: {timezone}")

        # Set seaborn theme
        sns.set_theme(style="whitegrid")

        # Convert to local timezone
        tz = pytz.timezone(timezone)
        df["timestamp_local"] = df["timestamp"].dt.tz_convert(tz)

        # Create plot
        plt.figure(figsize=(14, 6))
        plt.plot(
            df["timestamp_local"],
            df["base_fee_gwei"],
            label="Real Base Fee (GWEI)",
            color="#2a9d8f",
            linewidth=2
        )
        plt.plot(
            df["timestamp_local"],
            df["predicted_fee"],
            label="Predicted Base Fee (GWEI)",
            color="#e76f51",
            linewidth=2,
            linestyle="--"
        )

        # Add plot details
        plt.title(
            f"🎯 Real vs Predicted Ethereum Gas Fee ({timezone.split('/')[-1]})",
            fontsize=16,
            fontweight="bold"
        )
        plt.xlabel(f"Time ({timezone.split('/')[-1]})", fontsize=12)
        plt.ylabel("Base Fee (GWEI)", fontsize=12)
        plt.xticks(rotation=30)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %H:%M'))
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()

        # Calculate error metrics
        mae = (df["base_fee_gwei"] - df["predicted_fee"]).abs().mean()
        rmse = ((df["base_fee_gwei"] - df["predicted_fee"]) ** 2).mean() ** 0.5

        # Add error metrics to plot
        plt.figtext(
            0.01, 0.01,
            f"MAE: {mae:.2f} GWEI | RMSE: {rmse:.2f} GWEI",
            fontsize=10,
            bbox={"facecolor": "white", "alpha": 0.8, "pad": 5}
        )

        # Save or show plot
        if save_path:
            logger.info(f"Saving comparison plot to {save_path}")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        else:
            plt.show()

        return plt.gcf()
    except Exception as e:
        logger.error(f"Error creating comparison plot: {e}")
        raise

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Visualize comparison of real vs predicted gas fees")
    parser.add_argument("-f", "--file", type=str, default="data/gas_fees_with_predictions.csv",
                        help="Input data file path (default: data/gas_fees_with_predictions.csv)")
    parser.add_argument("-t", "--timezone", type=str, default="Asia/Kolkata",
                        help="Timezone for visualization (default: Asia/Kolkata)")
    parser.add_argument("-s", "--save", type=str, default=None,
                        help="Save plot to file path (default: None)")
    return parser.parse_args()

def main(data_path="data/gas_fees_with_predictions.csv", timezone="Asia/Kolkata", save_path=None):
    """Main function to create comparison visualization."""
    try:
        # Load data
        df = load_data(data_path)

        # Create comparison plot
        create_comparison_plot(df, timezone, save_path)

        return 0
    except Exception as e:
        logger.error(f"Error in visualization: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    args = parse_arguments()
    exit(main(args.file, args.timezone, args.save))
