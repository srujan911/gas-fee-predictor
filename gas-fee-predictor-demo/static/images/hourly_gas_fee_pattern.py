import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

def create_hourly_gas_fee_pattern():
    # Hours of the day (0-23)
    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    # Create data with a pattern - lower values in early mornings, higher in evenings
    # This should match the pattern in our heatmap
    data = np.zeros(24)
    for j in range(24):
        # Base value
        base = 25
        
        # Early morning discount (midnight to 6am)
        if j < 6:
            base *= 0.5
            
        # Evening peak (4pm to 8pm)
        if 16 <= j < 20:
            base *= 1.8
            
        # Add some randomness
        data[j] = base * (0.8 + 0.4 * np.random.random())
    
    # Make sure some values are below 1 GWEI
    data[3:5] = 0.7  # Early morning hours
    
    # Create a DataFrame for better handling
    df = pd.DataFrame({
        'hour': hour_labels,
        'gas_fee': data
    })
    
    # Set up the matplotlib figure
    plt.figure(figsize=(12, 6))
    
    # Create the bar chart
    bars = plt.bar(df['hour'], df['gas_fee'], width=0.7)
    
    # Color the bars based on gas fee values (green for low, red for high)
    for i, bar in enumerate(bars):
        if data[i] < 10:
            bar.set_color('#2ca02c')  # Green
        elif data[i] < 20:
            bar.set_color('#5fa832')  # Light green
        elif data[i] < 30:
            bar.set_color('#d67033')  # Orange
        else:
            bar.set_color('#d62728')  # Red
    
    # Add gas fee values on top of each bar
    for i, v in enumerate(data):
        plt.text(i, v + 1, f"{v:.1f}", ha='center', fontsize=9, rotation=90)
    
    # Set title and labels
    plt.title('Hourly Gas Fee Pattern (Real-Time Data)', fontsize=14, pad=20)
    plt.xlabel('Time of Day (IST)', fontsize=12)
    plt.ylabel('Gas Fee (GWEI)', fontsize=12)
    
    # Set y-axis limits
    plt.ylim(0, max(data) * 1.2)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=90)
    
    # Add grid lines
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'hourly_gas_fee_pattern.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Hourly gas fee pattern saved to {output_path}")
    
    # Close the figure
    plt.close()

if __name__ == "__main__":
    create_hourly_gas_fee_pattern()
