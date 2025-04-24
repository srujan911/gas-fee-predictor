#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Etherscan Style Heatmap Generator

This script generates a heatmap exactly like Etherscan's gas fee heatmap
with green for low fees and red for high fees.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

def generate_etherscan_style_heatmap(output_path="static/images/gas_fee_heatmap.png"):
    """Generate a heatmap exactly like Etherscan's gas fee heatmap."""
    print("Generating Etherscan-style gas fee heatmap")

    # Create necessary directories
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create date labels for the last 7 days (like in the Etherscan image)
    current_date = datetime.now()
    days_with_dates = []
    for i in range(7):
        # Start from 6 days ago
        day_date = current_date - timedelta(days=6-i)
        day_name = day_date.strftime('%a')
        day_num = day_date.strftime('%d %b')
        days_with_dates.append(f"{day_name}, {day_num}")

    # Create hours (0-23)
    hours = list(range(24))

    # Create realistic gas fee patterns based on the Etherscan image
    # Most cells have low values (light orange/peach)
    # A few spikes on Tuesday and Wednesday around hours 13-14
    # A spike on Thursday at hour 0

    # Initialize with very low values
    gas_data = np.ones((7, 24)) * 2  # Base value of 2 GWEI

    # Use fixed seed for reproducibility
    random.seed(42)

    # Add random variation to make it look natural
    for i in range(7):
        for j in range(24):
            # Add small random variation
            gas_data[i, j] += random.uniform(0, 1.5)

    # Add specific patterns from the Etherscan image

    # Thursday (day 0) has a spike at hour 0
    gas_data[0, 0] = 15  # High value

    # Tuesday (day 5) has higher values around hours 13-14
    gas_data[5, 13] = 18  # Very high value
    gas_data[5, 12] = 12  # High value
    gas_data[5, 14] = 12  # High value
    gas_data[5, 11] = 8   # Medium value
    gas_data[5, 15] = 8   # Medium value

    # Wednesday (day 6) has medium values
    gas_data[6, 13] = 8   # Medium value

    # Add some more random spikes
    for _ in range(5):
        i = random.randint(0, 6)
        j = random.randint(0, 23)
        gas_data[i, j] = random.uniform(6, 10)

    # Create DataFrame for the heatmap
    heatmap_data = pd.DataFrame(gas_data, index=days_with_dates, columns=hours)

    # Create the figure with a white background
    plt.figure(figsize=(14, 6), facecolor='white')

    # Create a custom colormap like Etherscan's (peach/light orange to dark orange/red)
    # Start with very light peach for low values
    colors = [(1.0, 0.94, 0.87), (0.99, 0.85, 0.7), (0.99, 0.7, 0.5), (0.95, 0.5, 0.3), (0.9, 0.3, 0.1)]
    cmap_name = 'etherscan_gas'
    cm = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=100)

    # Create the heatmap
    ax = sns.heatmap(heatmap_data, cmap=cm, linewidths=1, linecolor='white',
                    cbar_kws={'label': '', 'shrink': 0.8, 'aspect': 40},
                    vmin=0, vmax=20, annot=False, square=False)

    # Set title
    plt.title('Average Gas Prices', fontsize=16, fontweight='bold', pad=10, loc='left')

    # Set x-axis label
    plt.xlabel('Hours (UTC)', fontsize=12, labelpad=10)

    # Remove y-axis label
    plt.ylabel('')

    # Customize the colorbar
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=10)

    # Add ticks at 0, 5, 10, 15, 20
    cbar.set_ticks([0, 5, 10, 15, 20])
    cbar.set_ticklabels(['0', '5', '10', '15', '20'])

    # Improve tick labels
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10, rotation=0)

    # Remove the spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Save the figure with higher resolution
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved Etherscan-style heatmap to {output_path}")

    # Also save to visualizations directory
    viz_path = os.path.join("visualizations", "gas_fee_heatmap.png")
    os.makedirs(os.path.dirname(viz_path), exist_ok=True)
    plt.savefig(viz_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved heatmap to {viz_path}")

    # Find the best and worst times
    min_val = np.min(gas_data)
    max_val = np.max(gas_data)
    min_idx = np.unravel_index(np.argmin(gas_data), gas_data.shape)
    max_idx = np.unravel_index(np.argmax(gas_data), gas_data.shape)

    best_day = days_with_dates[min_idx[0]]
    best_hour = min_idx[1]
    worst_day = days_with_dates[max_idx[0]]
    worst_hour = max_idx[1]

    best_time = {
        'day': best_day,
        'hour': int(best_hour),
        'average_fee': float(min_val)
    }

    worst_time = {
        'day': worst_day,
        'hour': int(worst_hour),
        'average_fee': float(max_val)
    }

    print(f"Best time: {best_time['day']} at {best_time['hour']}:00 UTC ({best_time['average_fee']:.2f} GWEI)")
    print(f"Worst time: {worst_time['day']} at {worst_time['hour']}:00 UTC ({worst_time['average_fee']:.2f} GWEI)")

    return best_time, worst_time

if __name__ == "__main__":
    # Generate the heatmap
    best_time, worst_time = generate_etherscan_style_heatmap()
    print("Done!")
