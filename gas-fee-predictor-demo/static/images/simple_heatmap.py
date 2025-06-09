import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os

# Create a very simple heatmap
def create_simple_heatmap():
    # Days of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Hours of the day (0-23)
    hours = [f"{h:02d}:00" for h in range(24)]

    # Create data with a pattern - lower values on weekends and early mornings
    data = np.zeros((7, 24))
    for i in range(7):
        for j in range(24):
            # Base value
            base = 25

            # Weekend discount
            if i >= 5:  # Saturday and Sunday
                base *= 0.7

            # Early morning discount (midnight to 6am)
            if j < 6:
                base *= 0.6

            # Evening peak (4pm to 8pm)
            if 16 <= j < 20:
                base *= 1.5

            # Add some randomness
            data[i, j] = base * (0.9 + 0.2 * np.random.random())

    # Create a custom colormap from green to red
    cmap = sns.color_palette("RdYlGn_r", as_cmap=True)

    # Create a DataFrame for better labeling
    df = pd.DataFrame(data, index=days, columns=hours)

    # Plot the heatmap
    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(df, cmap=cmap, annot=True, fmt=".1f",
                     xticklabels=hours, yticklabels=days)

    plt.title('Ethereum Gas Fee Heatmap by Day and Hour (IST)', fontsize=16)
    plt.xlabel('Hour of Day (IST)')
    plt.ylabel('Day of Week')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Save the figure with absolute path
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'heatmap.png')
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"Simple heatmap saved to {output_path}")

    # Close the figure
    plt.close()

if __name__ == "__main__":
    create_simple_heatmap()
