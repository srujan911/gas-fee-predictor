#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Data Cleaning Script

This script cleans and preprocesses the raw Ethereum gas fee data collected from the blockchain.
It handles missing values, duplicates, timestamp conversion, and outlier detection.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_data(input_path="data/gas_fees.csv"):
    """Load the raw gas fee data from CSV."""
    try:
        logger.info(f"Loading data from: {input_path}")
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        df = pd.read_csv(input_path)
        logger.info(f"Loaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def handle_missing_values(df):
    """Handle missing values in the dataset."""
    try:
        logger.info("Handling missing values")
        initial_shape = df.shape


        missing_values = df.isnull().sum()
        logger.info(f"Missing values per column:\n{missing_values}")


        df.dropna(inplace=True)
        logger.info(f"After dropping missing values, shape: {df.shape}")
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} rows with missing values")

        return df
    except Exception as e:
        logger.error(f"Error handling missing values: {e}")
        raise

def handle_duplicates(df):
    """Remove duplicate rows from the dataset."""
    try:
        logger.info("Removing duplicate rows")
        initial_shape = df.shape


        df.drop_duplicates(inplace=True)
        logger.info(f"After dropping duplicates, shape: {df.shape}")
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows")

        return df
    except Exception as e:
        logger.error(f"Error handling duplicates: {e}")
        raise

def convert_timestamps(df):
    """Convert timestamp strings to datetime objects."""
    try:
        logger.info("Converting timestamp column to datetime")


        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')


        initial_shape = df.shape
        df.dropna(subset=["timestamp"], inplace=True)
        logger.info(f"After removing invalid timestamps, shape: {df.shape}")
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} rows with invalid timestamps")


        logger.info(f"Timestamp conversion preview: {df['timestamp'].head()}")

        return df
    except Exception as e:
        logger.error(f"Error converting timestamps: {e}")
        raise

def detect_outliers(df, column="base_fee_gwei", z_threshold=3.0):
    """Detect and handle outliers in the specified column using Z-score."""
    try:
        logger.info(f"Detecting outliers in {column} using Z-score method")


        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        outliers = z_scores > z_threshold

        logger.info(f"Found {outliers.sum()} outliers in {column} (Z-score > {z_threshold})")


        plt.figure(figsize=(12, 6))


        plt.subplot(1, 2, 1)
        sns.boxplot(x=df[column])
        plt.title(f"Box Plot of {column}")


        plt.subplot(1, 2, 2)
        sns.histplot(df[column], kde=True)
        mean = df[column].mean()
        std = df[column].std()
        plt.axvline(mean + z_threshold * std, color='r', linestyle='--',
                   label=f'Z-score = {z_threshold}')
        plt.axvline(mean - z_threshold * std, color='r', linestyle='--')
        plt.legend()
        plt.title(f"Distribution of {column} with Outlier Thresholds")

        plt.tight_layout()


        os.makedirs("data/plots", exist_ok=True)
        plt.savefig(f"data/plots/{column}_outliers.png")
        logger.info(f"Outlier plot saved to data/plots/{column}_outliers.png")


        upper_bound = df[column].mean() + z_threshold * df[column].std()
        lower_bound = df[column].mean() - z_threshold * df[column].std()
        df_clean = df.copy()
        df_clean.loc[df_clean[column] > upper_bound, column] = upper_bound
        df_clean.loc[df_clean[column] < lower_bound, column] = lower_bound
        logger.info(f"Capped outliers in {column} to range [{lower_bound:.2f}, {upper_bound:.2f}]")

        return df_clean
    except Exception as e:
        logger.error(f"Error detecting outliers: {e}")
        logger.info("Continuing without outlier detection")
        return df

def sort_and_save_data(df, output_path="data/gas_fees_cleaned.csv"):
    """Sort the data by block number and save to CSV."""
    try:
        logger.info("Sorting data by block_number")
        df.sort_values("block_number", inplace=True)

        if df.empty:
            logger.warning("No data to save after cleaning")
            return False


        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Saving cleaned data to: {output_path}")
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned data saved successfully with shape: {df.shape}")


        stats_path = os.path.join(os.path.dirname(output_path), "gas_fees_stats.txt")
        with open(stats_path, 'w') as f:
            f.write("Gas Fee Data Summary Statistics\n")
            f.write("============================\n\n")
            f.write(f"Total Records: {df.shape[0]}\n")
            f.write(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}\n\n")
            f.write("Statistical Summary:\n")
            f.write(df.describe().to_string())

        logger.info(f"Summary statistics saved to {stats_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise

def clean_gas_data(input_path="data/gas_fees.csv", output_path="data/gas_fees_cleaned.csv"):
    """Main function to clean the gas fee data."""
    try:

        df = load_data(input_path)


        df = handle_missing_values(df)


        df = handle_duplicates(df)


        df = convert_timestamps(df)


        df = detect_outliers(df, column="base_fee_gwei")


        success = sort_and_save_data(df, output_path)

        if success:
            print("\n" + "=" * 50)
            print("🔮 ETHEREUM GAS FEE DATA CLEANING 🔮")
            print("=" * 50)
            print(f"✅ Data cleaning completed successfully!")
            print(f"📃 Initial data shape: {load_data(input_path).shape}")
            print(f"📄 Final data shape: {df.shape}")
            print(f"💾 Cleaned data saved to: {output_path}")
            print("=" * 50)
        else:
            print("❌ No data to save after cleaning.")

        return df
    except Exception as e:
        logger.error(f"Error in data cleaning pipeline: {e}")
        print(f"❌ Error cleaning data: {e}")
        return None

if __name__ == "__main__":
    clean_gas_data()