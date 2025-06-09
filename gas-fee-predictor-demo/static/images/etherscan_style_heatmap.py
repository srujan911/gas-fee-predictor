import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
from matplotlib.colors import LinearSegmentedColormap

# Create a heatmap that looks like Etherscan's
def create_etherscan_style_heatmap():
    # Days of the week
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    
    # Hours of the day (0-23)
    hours = list(range(24))
    
    # Create data with a pattern - lower values on weekends and early mornings
    data = np.zeros((7, 24))
    for i in range(7):
        for j in range(24):
            # Base value
            base = 25
            
            # Weekend discount (Saturday and Sunday)
            if i == 0 or i == 6:  # Sunday (0) and Saturday (6)
                base *= 0.4
                
            # Early morning discount (midnight to 6am)
            if j < 6:
                base *= 0.5
                
            # Evening peak (4pm to 8pm)
            if 16 <= j < 20:
                base *= 1.8
                
            # Add some randomness
            data[i, j] = base * (0.8 + 0.4 * np.random.random())
    
    # Make sure some values are below 1 GWEI
    data[0, 3:5] = 0.3  # Sunday early morning
    data[6, 3:5] = 0.4  # Saturday early morning
    
    # Create a custom colormap from green to red (Etherscan style)
    colors = [(0.0, 0.5, 0.0), (0.9, 0.9, 0.0), (0.8, 0.4, 0.0), (0.8, 0.0, 0.0)]
    cmap = LinearSegmentedColormap.from_list('etherscan', colors, N=100)
    
    # Create a DataFrame for better labeling
    df = pd.DataFrame(data, index=days, columns=[f"{h}" for h in hours])
    
    # Plot the heatmap
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(df, cmap=cmap, annot=True, fmt=".1f", 
                     linewidths=0.5, cbar_kws={'label': 'Gas Price (GWEI)'})
    
    plt.title('Ethereum Gas Price Heatmap (IST)', fontsize=16, pad=20)
    plt.xlabel('Hour of Day (IST)', fontsize=12)
    plt.ylabel('Day of Week', fontsize=12)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'heatmap.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Etherscan-style heatmap saved to {output_path}")
    
    # Close the figure
    plt.close()

if __name__ == "__main__":
    create_etherscan_style_heatmap()
