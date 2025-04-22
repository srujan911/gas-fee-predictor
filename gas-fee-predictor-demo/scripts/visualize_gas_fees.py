#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Gas Fee Visualization

This script creates visualizations of Ethereum gas fees over time and by hour of day.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import pytz
import plotly.express as px
import plotly.graph_objects as go
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_data(file_path="data/gas_fees_cleaned.csv"):
    """Load and preprocess gas fee data."""
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df = df.dropna(subset=["timestamp"])

        logger.info(f"Loaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def create_time_series_plot(df, timezone="Asia/Kolkata", save_path=None):
    """Create a time series plot of gas fees."""
    try:
        logger.info(f"Creating time series plot with timezone: {timezone}")

        # Convert to local timezone
        tz = pytz.timezone(timezone)
        df["timestamp_local"] = df["timestamp"].dt.tz_convert(tz)

        # Create plot
        fig = px.line(
            df,
            x="timestamp_local",
            y="base_fee_gwei",
            title=f"📈 Ethereum Base Fee Over Time ({timezone.split('/')[-1]})",
            labels={"timestamp_local": f"Time ({timezone.split('/')[-1]})", "base_fee_gwei": "Base Fee (GWEI)"},
            template="plotly_dark",
        )

        fig.update_traces(
            line=dict(color="#00CC96", width=2),
            hovertemplate="Time: %{x}<br>Fee: %{y:.2f} GWEI"
        )

        fig.update_layout(
            title_font_size=20,
            xaxis_title_font_size=16,
            yaxis_title_font_size=16
        )

        # Save or show plot
        if save_path:
            logger.info(f"Saving time series plot to {save_path}")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_image(save_path)
            fig.write_html(save_path.replace('.png', '.html'))
        else:
            fig.show()

        return fig
    except Exception as e:
        logger.error(f"Error creating time series plot: {e}")
        raise

def create_hourly_bar_plot(df, timezone="Asia/Kolkata", save_path=None):
    """Create a bar plot of average gas fees by hour of day."""
    try:
        logger.info(f"Creating hourly bar plot with timezone: {timezone}")

        # Convert to local timezone if not already done
        if "timestamp_local" not in df.columns:
            tz = pytz.timezone(timezone)
            df["timestamp_local"] = df["timestamp"].dt.tz_convert(tz)

        # Extract hour of day and calculate hourly average
        df["hour_of_day_local"] = df["timestamp_local"].dt.hour
        hourly_fee = df.groupby("hour_of_day_local")["base_fee_gwei"].mean().reindex(range(24), fill_value=0).reset_index()

        # Create plot
        fig = px.bar(
            hourly_fee,
            x="hour_of_day_local",
            y="base_fee_gwei",
            title=f"🕒 Average Ethereum Gas Fee by Hour ({timezone.split('/')[-1]})",
            labels={"hour_of_day_local": f"Hour ({timezone.split('/')[-1]})", "base_fee_gwei": "Average Base Fee (GWEI)"},
            color="base_fee_gwei",
            color_continuous_scale="Viridis",
            template="plotly_dark",
        )

        fig.update_traces(hovertemplate="Hour: %{x}h<br>Fee: %{y:.2f} GWEI")

        fig.update_layout(
            title_font_size=20,
            xaxis_title_font_size=16,
            yaxis_title_font_size=16
        )

        # Save or show plot
        if save_path:
            logger.info(f"Saving hourly bar plot to {save_path}")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_image(save_path)
            fig.write_html(save_path.replace('.png', '.html'))
        else:
            fig.show()

        return fig
    except Exception as e:
        logger.error(f"Error creating hourly bar plot: {e}")
        raise

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Visualize Ethereum gas fees")
    parser.add_argument("-f", "--file", type=str, default="data/gas_fees_cleaned.csv",
                        help="Input data file path (default: data/gas_fees_cleaned.csv)")
    parser.add_argument("-t", "--timezone", type=str, default="Asia/Kolkata",
                        help="Timezone for visualization (default: Asia/Kolkata)")
    parser.add_argument("-s", "--save", type=str, default=None,
                        help="Save plots to directory (default: None)")
    return parser.parse_args()

def main(data_path="data/gas_fees_cleaned.csv", timezone="Asia/Kolkata", save_path=None):
    """Main function to create visualizations."""
    try:
        # Load data
        df = load_data(data_path)

        # Create time series plot
        time_series_path = None
        if save_path:
            time_series_path = os.path.join(save_path) if save_path.endswith('.png') else \
                              os.path.join(save_path, "gas_fees_time_series.png")
        time_series_fig = create_time_series_plot(df, timezone, time_series_path)

        # Create hourly bar plot
        hourly_path = None
        if save_path:
            if save_path.endswith('.png'):
                hourly_path = save_path.replace('.png', '_hourly.png')
            else:
                hourly_path = os.path.join(save_path, "gas_fees_hourly.png")
        hourly_fig = create_hourly_bar_plot(df, timezone, hourly_path)

        return 0
    except Exception as e:
        logger.error(f"Error in visualization: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    args = parse_arguments()
    exit(main(args.file, args.timezone, args.save))
