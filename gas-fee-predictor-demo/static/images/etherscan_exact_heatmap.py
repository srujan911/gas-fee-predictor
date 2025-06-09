import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import os

# Create a heatmap with exact Etherscan data from the screenshot
def create_etherscan_exact_heatmap(output_path):
    # Days of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Hours of the day (0-23)
    hours = list(range(24))

    # Exact Etherscan data from the screenshot
    data = np.array([
        # Monday
        [14.3, 16.4, 15.9, 15.9, 15.4, 13.2, 24.0, 24.6, 23.2, 23.4, 25.9, 24.7, 25.4, 22.6, 24.7, 24.1, 38.3, 40.2, 39.7, 38.1, 23.7, 24.7, 26.4, 24.9],
        # Tuesday
        [14.1, 15.6, 15.0, 14.1, 13.8, 14.9, 16.5, 27.4, 26.3, 24.0, 27.4, 23.9, 24.4, 26.2, 23.4, 22.8, 27.3, 36.1, 40.1, 35.5, 37.6, 23.6, 23.6, 23.8],
        # Wednesday
        [14.1, 15.6, 14.6, 13.9, 14.9, 16.3, 27.4, 25.2, 25.6, 25.4, 26.5, 26.1, 25.2, 27.4, 25.0, 27.0, 35.7, 37.0, 34.3, 34.7, 24.6, 26.1, 26.6, 26.6],
        # Thursday
        [13.7, 16.0, 14.9, 14.2, 15.7, 16.0, 27.1, 26.2, 26.8, 24.9, 23.7, 25.6, 26.1, 23.9, 27.0, 27.0, 37.2, 40.7, 36.5, 38.5, 23.9, 26.3, 25.4, 25.3],
        # Friday
        [14.9, 15.8, 14.5, 15.5, 16.2, 15.1, 24.5, 24.0, 24.7, 22.8, 25.4, 25.4, 26.2, 24.6, 25.6, 24.6, 39.0, 40.6, 36.3, 34.8, 26.1, 23.3, 25.8, 27.5],
        # Saturday
        [11.1, 9.5, 9.5, 10.1, 10.2, 11.3, 18.4, 18.3, 18.1, 16.4, 17.0, 18.1, 18.4, 17.9, 17.4, 17.9, 26.1, 24.1, 24.6, 24.4, 18.0, 16.0, 18.3, 17.6],
        # Sunday
        [11.3, 9.7, 11.2, 9.5, 10.9, 10.3, 16.2, 16.4, 19.0, 16.4, 16.3, 19.0, 16.7, 16.7, 18.0, 16.4, 25.4, 25.5, 27.0, 27.0, 17.7, 16.7, 17.7, 17.5]
    ])

    # Find the best and worst times
    min_idx = np.unravel_index(data.argmin(), data.shape)
    max_idx = np.unravel_index(data.argmax(), data.shape)

    best_day = days[min_idx[0]]
    best_hour = min_idx[1]
    best_fee = data[min_idx]

    worst_day = days[max_idx[0]]
    worst_hour = max_idx[1]
    worst_fee = data[max_idx]

    print(f"Best time: {best_day} at {best_hour:02d}:00 - {best_fee:.4f} GWEI")
    print(f"Worst time: {worst_day} at {worst_hour:02d}:00 - {worst_fee:.4f} GWEI")

    # Create a DataFrame for better labeling
    df = pd.DataFrame(data, index=days, columns=[f"{h:02d}:00" for h in hours])

    # Set up the matplotlib figure
    plt.figure(figsize=(12, 8))

    # Create a custom colormap from green to red
    cmap = sns.color_palette("RdYlGn_r", as_cmap=True)

    # Plot the heatmap
    ax = sns.heatmap(df, cmap=cmap, annot=True, fmt=".1f", linewidths=0.5,
                     cbar_kws={'label': 'Average Gas Fee (GWEI)'})

    # Set title and labels
    plt.title('Ethereum Gas Fee Heatmap by Day and Hour (IST)', fontsize=16, pad=20)
    plt.xlabel('Hour of Day (IST)', fontsize=12, labelpad=10)
    plt.ylabel('Day of Week', fontsize=12, labelpad=10)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add source attribution
    plt.figtext(0.5, 0.01, "Source: Etherscan Gas Fee Heatmap (IST Timezone)",
                ha='center', fontsize=10, color='gray')

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Heatmap saved to {output_path}")

    # Close the figure to free memory
    plt.close()

    return {
        'best_time': {'day': best_day, 'hour': best_hour, 'fee': float(best_fee)},
        'worst_time': {'day': worst_day, 'hour': worst_hour, 'fee': float(worst_fee)}
    }

if __name__ == "__main__":
    import pandas as pd

    # Ensure the output directory exists
    output_dir = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(output_dir, exist_ok=True)

    # Create and save the heatmap
    output_path = os.path.join(output_dir, 'gas_fee_heatmap.png')
    results = create_etherscan_exact_heatmap(output_path)

    print(f"Best time: {results['best_time']['day']} at {results['best_time']['hour']:02d}:00 - {results['best_time']['fee']:.4f} GWEI")
    print(f"Worst time: {results['worst_time']['day']} at {results['worst_time']['hour']:02d}:00 - {results['worst_time']['fee']:.4f} GWEI")
