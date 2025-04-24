"""
Direct Heatmap Generator for Ethereum Gas Fees

This script generates a heatmap of Ethereum gas fees directly from the data,
without requiring pre-processing or data cleaning. It's designed to be used
as a standalone script or imported as a module.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import matplotlib.dates as mdates

def load_gas_fee_data(file_path='data/historical_gas_data.csv'):
    """
    Load historical gas fee data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing historical gas fee data
        
    Returns:
        DataFrame containing historical gas fee data
    """
    try:
        if not os.path.exists(file_path):
            print(f"Warning: Historical data file not found at {file_path}")
            return None
            
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime if it's not already
        if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        print(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading gas fee data: {e}")
        return None

def generate_heatmap(df=None, output_path='static/images/gas_fee_heatmap.png', cmap='YlOrRd', timezone='UTC'):
    """
    Generate a heatmap of gas fees by day of week and hour of day.
    
    Args:
        df: DataFrame containing historical gas fee data (optional)
        output_path: Path to save the generated heatmap image
        cmap: Colormap to use for the heatmap
        timezone: Timezone to use for the heatmap
        
    Returns:
        Tuple of (best_time, worst_time) strings
    """
    try:
        if df is None:
            # Load data if not provided
            df = load_gas_fee_data()
            
        if df is None:
            print("No data available. Generating sample data for demonstration.")
            
            # Generate sample data for demonstration
            np.random.seed(42)
            timestamps = pd.date_range(start='2025-04-01', periods=168, freq='H')  # 7 days of hourly data
            
            # Create realistic gas fee pattern
            base_value = 50
            hourly_pattern = np.sin(np.arange(24) * 2 * np.pi / 24) * 10 + base_value
            daily_pattern = np.array([1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 0.8])  # Mon-Sun multiplier
            
            gas_fees = []
            for ts in timestamps:
                hour_factor = hourly_pattern[ts.hour]
                day_factor = daily_pattern[ts.dayofweek]
                random_factor = np.random.normal(1, 0.1)  # Add some randomness
                gas_fees.append(hour_factor * day_factor * random_factor)
            
            # Create sample DataFrame
            df = pd.DataFrame({
                'timestamp': timestamps,
                'base_fee_gwei': gas_fees
            })
            
            print("Generated sample data for demonstration.")
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must contain a 'timestamp' column")
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            raise ValueError("DataFrame must contain either 'gas_fee' or 'base_fee_gwei' column")
            
        # Convert timezone if needed
        if timezone != 'UTC':
            try:
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(timezone)
                print(f"Converted timestamps to {timezone} timezone")
            except Exception as e:
                print(f"Error converting timezone: {e}")
                print("Using UTC timezone instead")
                
        # Extract day of week and hour from timestamp
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['hour'] = df['timestamp'].dt.hour
        
        # Create pivot table for heatmap
        pivot_table = df.pivot_table(
            values=gas_fee_col,
            index='day_of_week',
            columns='hour',
            aggfunc='mean'
        )
        
        # Reorder days of week
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_table = pivot_table.reindex(days_order)
        
        # Create figure and axes
        plt.figure(figsize=(12, 8))
        
        # Generate heatmap
        ax = sns.heatmap(
            pivot_table,
            cmap=cmap,
            annot=True,
            fmt='.1f',
            linewidths=0.5,
            cbar_kws={'label': 'Average Gas Fee (GWEI)'}
        )
        
        # Set title and labels
        plt.title('Average Ethereum Gas Fees by Day and Hour (GWEI)', fontsize=16)
        plt.xlabel(f'Hour of Day ({timezone})', fontsize=12)
        plt.ylabel('Day of Week', fontsize=12)
        
        # Adjust tick labels
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        
        # Create directory for output if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Heatmap saved to {output_path}")
        
        # Find best and worst times to transact
        min_value = pivot_table.min().min()
        max_value = pivot_table.max().max()
        
        min_indices = np.where(pivot_table.values == min_value)
        max_indices = np.where(pivot_table.values == max_value)
        
        best_day = pivot_table.index[min_indices[0][0]]
        best_hour = pivot_table.columns[min_indices[1][0]]
        
        worst_day = pivot_table.index[max_indices[0][0]]
        worst_hour = pivot_table.columns[max_indices[1][0]]
        
        best_time = f"{best_day} at {best_hour:02d}:00 (Average: {min_value:.2f} GWEI)"
        worst_time = f"{worst_day} at {worst_hour:02d}:00 (Average: {max_value:.2f} GWEI)"
        
        return best_time, worst_time
        
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        return "Unknown", "Unknown"

def main():
    """Main function to run the heatmap generator."""
    try:
        # Generate heatmap
        best_time, worst_time = generate_heatmap(timezone='Asia/Kolkata')
        
        # Print results
        print(f"Best time to transact: {best_time}")
        print(f"Worst time to transact: {worst_time}")
        print("Done!")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
