import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import os

# Create a custom heatmap that looks like Etherscan's
def create_etherscan_style_heatmap(output_path):
    # Days of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Hours of the day (0-23)
    hours = list(range(24))
    
    # Create a sample data matrix (7x24) with realistic gas fee patterns
    # Lower values on weekends and early mornings, higher values during weekdays and peak hours
    data = np.zeros((7, 24))
    
    # Base values - weekdays have higher base values
    for i, day in enumerate(days):
        if day in ['Saturday', 'Sunday']:
            # Weekend base is lower
            data[i, :] = np.random.uniform(15, 20, 24)
        else:
            # Weekday base is higher
            data[i, :] = np.random.uniform(20, 25, 24)
    
    # Hour patterns - early morning hours are lower, peak hours are higher
    for i in range(7):
        # Early morning hours (0-5) are lower
        data[i, 0:6] *= 0.7
        # Morning hours (6-11) gradually increase
        data[i, 6:12] *= np.linspace(0.8, 1.2, 6)
        # Afternoon hours (12-17) are peak
        data[i, 12:18] *= 1.3
        # Evening hours (18-23) gradually decrease
        data[i, 18:24] *= np.linspace(1.2, 0.9, 6)
    
    # Add some realistic patterns
    # Friday evening has higher gas fees
    data[4, 18:24] *= 1.4
    # Monday morning has higher gas fees
    data[0, 8:12] *= 1.3
    # Weekend mornings have lower gas fees
    data[5:7, 4:10] *= 0.6
    
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
    
    # Add timestamp
    plt.figtext(0.02, 0.02, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                fontsize=8, color='gray')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Heatmap saved to {output_path}")
    
    # Close the figure to free memory
    plt.close()

if __name__ == "__main__":
    # Ensure the output directory exists
    output_dir = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save the heatmap
    output_path = os.path.join(output_dir, 'gas_fee_heatmap.png')
    create_etherscan_style_heatmap(output_path)
