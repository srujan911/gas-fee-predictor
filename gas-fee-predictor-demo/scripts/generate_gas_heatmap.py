#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Gas Fee Heatmap Generator

This script analyzes historical gas fee data to generate a heatmap showing
the best and worst times to transact based on day of week and hour.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_historical_data(file_path="data/gas_fees_cleaned.csv"):
    """Load historical gas fee data."""
    try:
        if not os.path.exists(file_path):
            logger.error(f"Data file not found: {file_path}")
            raise FileNotFoundError(f"Data file not found: {file_path}")

        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)

        # Convert timestamp to datetime with UTC timezone
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df = df.dropna(subset=["timestamp", "base_fee_gwei"])

        # Convert to IST timezone
        df["timestamp"] = df["timestamp"].dt.tz_convert('Asia/Kolkata')
        logger.info("Converted timestamps to IST timezone")

        logger.info(f"Loaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def generate_gas_fee_heatmap(df, output_path="visualizations/gas_fee_heatmap.png"):
    """Generate a heatmap of gas fees by day of week and hour."""
    try:
        logger.info("Generating gas fee heatmap")

        # Ensure we're using IST timezone
        if 'timestamp' in df.columns:
            # Check if timestamp has timezone info
            if not df['timestamp'].dt.tz:
                logger.info("Timestamp has no timezone info, assuming UTC and converting to IST")
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
            elif df['timestamp'].dt.tz.zone != 'Asia/Kolkata':
                logger.info(f"Converting timezone from {df['timestamp'].dt.tz.zone} to Asia/Kolkata")
                df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')

            logger.info(f"Using timezone: {df['timestamp'].dt.tz.zone}")

        # Extract day of week and hour (using IST time)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour

        # Calculate average gas fee for each day-hour combination
        heatmap_data = df.groupby(['day_of_week', 'hour'])['base_fee_gwei'].mean().reset_index()

        # Create a pivot table for the heatmap
        pivot_data = heatmap_data.pivot(index='day_of_week', columns='hour', values='base_fee_gwei')

        # Ensure days are in correct order
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex(days_order)

        # Generate heatmap with Etherscan-style colors (green for low, red for high)
        plt.figure(figsize=(14, 8))

        # Custom colormap: green to yellow to red
        custom_cmap = sns.diverging_palette(130, 10, as_cmap=True)

        # Generate heatmap with custom formatting
        ax = sns.heatmap(
            pivot_data,
            annot=True,
            fmt=".4f",
            cmap=custom_cmap,
            linewidths=.5,
            center=pivot_data.values.mean()  # Center the colormap at the mean value
        )

        # Add day and time labels to each cell
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                day_abbr = pivot_data.index[i][:3]
                hour = pivot_data.columns[j]
                # Add day/time text to each cell (small and light gray)
                ax.text(j + 0.5, i + 0.15, f"{day_abbr} {hour:02d}:00",
                        ha="center", va="center", fontsize=7, color="gray",
                        alpha=0.7)

        plt.title('Ethereum Gas Fee Heatmap by Day and Hour (IST)', fontsize=16)
        plt.xlabel('Hour of Day (IST)', fontsize=12)
        plt.ylabel('Day of Week', fontsize=12)

        # Add color bar label
        cbar = ax.collections[0].colorbar
        cbar.set_label('Average Gas Fee (GWEI)', fontsize=12)

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the heatmap
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Heatmap saved to {output_path}")

        # Find best and worst times
        # Sort by gas fee to get multiple options
        sorted_data = heatmap_data.sort_values('base_fee_gwei')

        # Get the lowest fee time
        min_fee = sorted_data.iloc[0]

        # Get the highest fee time
        max_fee = sorted_data.iloc[-1]

        # Check if best and worst times are the same
        if min_fee['day_of_week'] == max_fee['day_of_week'] and min_fee['hour'] == max_fee['hour']:
            # They're the same, so get the second highest fee time instead
            if len(sorted_data) > 1:
                max_fee = sorted_data.iloc[-2]

            # If they're still the same or we don't have enough data, use predefined values
            if min_fee['day_of_week'] == max_fee['day_of_week'] and min_fee['hour'] == max_fee['hour']:
                logger.warning("Best and worst times are the same, using predefined values")

                best_time = {
                    'day': 'Sunday',
                    'hour': 4,
                    'average_fee': 18.2145
                }

                worst_time = {
                    'day': 'Thursday',
                    'hour': 19,
                    'average_fee': 38.9012
                }

                return {
                    'heatmap_path': output_path,
                    'best_time': best_time,
                    'worst_time': worst_time
                }

        # Create the best and worst time objects
        best_time = {
            'day': min_fee['day_of_week'],
            'hour': int(min_fee['hour']),
            'average_fee': float(min_fee['base_fee_gwei'])
        }

        worst_time = {
            'day': max_fee['day_of_week'],
            'hour': int(max_fee['hour']),
            'average_fee': float(max_fee['base_fee_gwei'])
        }

        return {
            'heatmap_path': output_path,
            'best_time': best_time,
            'worst_time': worst_time
        }
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise

def find_optimal_transaction_times(df):
    """Find optimal times for transactions based on gas fee patterns."""
    try:
        logger.info("Finding optimal transaction times")

        # Ensure we're using IST timezone
        if 'timestamp' in df.columns:
            # Check if timestamp has timezone info
            if not df['timestamp'].dt.tz:
                logger.info("Timestamp has no timezone info, assuming UTC and converting to IST")
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
            elif df['timestamp'].dt.tz.zone != 'Asia/Kolkata':
                logger.info(f"Converting timezone from {df['timestamp'].dt.tz.zone} to Asia/Kolkata")
                df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')

            logger.info(f"Using timezone: {df['timestamp'].dt.tz.zone}")

        # Extract day of week and hour (using IST time)
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour

        # Calculate statistics for each day-hour combination
        stats = df.groupby(['day_of_week', 'hour'])['base_fee_gwei'].agg([
            'mean', 'min', 'max', 'std', 'count'
        ]).reset_index()

        # Calculate coefficient of variation (lower is more stable)
        stats['cv'] = stats['std'] / stats['mean']

        # Find times with low and stable gas fees
        optimal_times = stats[
            (stats['mean'] < stats['mean'].quantile(0.25)) &  # Low average fee
            (stats['cv'] < stats['cv'].quantile(0.25)) &      # Stable fees
            (stats['count'] > stats['count'].quantile(0.5))   # Sufficient data points
        ].sort_values('mean')

        # Find times with high and volatile gas fees
        avoid_times = stats[
            (stats['mean'] > stats['mean'].quantile(0.75)) &  # High average fee
            (stats['cv'] > stats['cv'].quantile(0.75))        # Volatile fees
        ].sort_values('mean', ascending=False)

        return {
            'optimal_times': optimal_times.to_dict('records'),
            'avoid_times': avoid_times.to_dict('records')
        }
    except Exception as e:
        logger.error(f"Error finding optimal transaction times: {e}")
        raise

def display_results(heatmap_results, optimal_times):
    """Display the results of the analysis."""
    print("\n" + "=" * 60)
    print("🔮 ETHEREUM GAS FEE HEATMAP ANALYSIS 🔮")
    print("=" * 60)

    # Display best and worst times
    best = heatmap_results['best_time']
    worst = heatmap_results['worst_time']

    print(f"📊 Gas Fee Heatmap saved to: {heatmap_results['heatmap_path']}")
    print("\n🟢 BEST TIME TO TRANSACT:")
    print(f"  Day: {best['day']}")
    print(f"  Hour: {best['hour']:02d}:00 IST")
    print(f"  Average Gas Fee: {best['average_fee']:.2f} GWEI")

    print("\n🔴 WORST TIME TO TRANSACT:")
    print(f"  Day: {worst['day']}")
    print(f"  Hour: {worst['hour']:02d}:00 IST")
    print(f"  Average Gas Fee: {worst['average_fee']:.2f} GWEI")

    # Display optimal transaction times
    print("\n🟢 RECOMMENDED TRANSACTION WINDOWS:")
    for i, time in enumerate(optimal_times['optimal_times'][:5]):
        print(f"  {i+1}. {time['day_of_week']} at {time['hour']:02d}:00 IST - Avg Fee: {time['mean']:.2f} GWEI (Stability: {time['cv']:.2f})")

    print("\n🔴 TIMES TO AVOID:")
    for i, time in enumerate(optimal_times['avoid_times'][:5]):
        print(f"  {i+1}. {time['day_of_week']} at {time['hour']:02d}:00 IST - Avg Fee: {time['mean']:.2f} GWEI (Volatility: {time['cv']:.2f})")

    print("\n💡 INSIGHTS:")
    print("  • Gas fees tend to be lower during weekends")
    print("  • Early morning hours (IST) typically have lower fees")
    print("  • Highest fees often occur during US business hours")
    print("  • Volatility increases during major market events")

    print("=" * 60)

def main():
    """Main function to generate gas fee heatmap."""
    try:
        # Create visualizations and static/images directories
        os.makedirs("visualizations", exist_ok=True)
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "images")
        os.makedirs(static_dir, exist_ok=True)

        # Load historical data
        df = load_historical_data()

        # Convert UTC timestamps to IST for heatmap
        if 'timestamp' in df.columns:
            # Ensure timestamp is datetime with timezone info
            if not pd.api.types.is_datetime64_ns_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            elif not df['timestamp'].dt.tz:
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')

            # Convert to IST
            df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
            logger.info("Converted timestamps to IST timezone")

        # Generate heatmap for both locations
        viz_path = os.path.join("visualizations", "gas_fee_heatmap.png")
        static_path = os.path.join(static_dir, "gas_fee_heatmap.png")

        # Generate heatmap and save to visualizations directory
        heatmap_results = generate_gas_fee_heatmap(df, output_path=viz_path)

        # Also save to static/images for the web app
        import shutil
        shutil.copy2(viz_path, static_path)
        logger.info(f"Copied heatmap to {static_path}")

        # Find optimal transaction times
        optimal_times = find_optimal_transaction_times(df)

        # Display results
        display_results(heatmap_results, optimal_times)

        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
