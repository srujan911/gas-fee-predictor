"""
Advanced Visualizations for Ethereum Gas Fee Analysis

This script creates advanced visualizations for Ethereum gas fee analysis,
including 3D plots, animated visualizations, and interactive charts.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta

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

def create_3d_surface_plot(df, output_path='visualizations/gas_fee_3d_surface.png'):
    """
    Create a 3D surface plot of gas fees by day and hour.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for 3D surface plot")
            return
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            print("Timestamp column not found in data")
            return
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return
            
        # Extract day of week and hour from timestamp
        df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['hour'] = df['timestamp'].dt.hour
        
        # Create pivot table for surface plot
        pivot_table = df.pivot_table(
            values=gas_fee_col,
            index='day_of_week',
            columns='hour',
            aggfunc='mean'
        )
        
        # Create figure
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create meshgrid
        X, Y = np.meshgrid(np.arange(pivot_table.shape[1]), np.arange(pivot_table.shape[0]))
        
        # Create surface plot
        surf = ax.plot_surface(X, Y, pivot_table.values, cmap='viridis', edgecolor='none', alpha=0.8)
        
        # Set labels and title
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Day of Week')
        ax.set_zlabel('Gas Fee (GWEI)')
        ax.set_title('3D Surface Plot of Gas Fees by Day and Hour')
        
        # Set x-axis ticks
        ax.set_xticks(np.arange(0, 24, 3))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 3)])
        
        # Set y-axis ticks
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ax.set_yticks(np.arange(7))
        ax.set_yticklabels(day_names)
        
        # Add color bar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Gas Fee (GWEI)')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"3D surface plot saved to {output_path}")
    except Exception as e:
        print(f"Error creating 3D surface plot: {e}")

def create_animated_time_series(df, output_path='visualizations/gas_fee_animated.gif'):
    """
    Create an animated time series visualization of gas fees.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for animated time series")
            return
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            print("Timestamp column not found in data")
            return
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return
            
        # Sort data by timestamp
        df = df.sort_values('timestamp')
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Set up plot
        line, = ax.plot([], [], lw=2)
        scatter = ax.scatter([], [], s=50, c='red')
        
        # Set labels and title
        ax.set_xlabel('Time')
        ax.set_ylabel('Gas Fee (GWEI)')
        ax.set_title('Animated Gas Fee Time Series')
        
        # Set axis limits
        ax.set_xlim(df['timestamp'].min(), df['timestamp'].max())
        ax.set_ylim(df[gas_fee_col].min() * 0.9, df[gas_fee_col].max() * 1.1)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Initialize function for animation
        def init():
            line.set_data([], [])
            scatter.set_offsets(np.empty((0, 2)))
            return line, scatter
        
        # Update function for animation
        def update(frame):
            # Get data up to current frame
            data = df.iloc[:frame]
            
            # Update line
            line.set_data(data['timestamp'], data[gas_fee_col])
            
            # Update scatter (only show the latest point)
            if len(data) > 0:
                latest = data.iloc[-1]
                scatter.set_offsets([[mdates.date2num(latest['timestamp']), latest[gas_fee_col]]])
            
            # Update title with current date
            if len(data) > 0:
                ax.set_title(f'Gas Fee Time Series - {latest["timestamp"].strftime("%Y-%m-%d %H:%M")}')
            
            return line, scatter
        
        # Create animation
        frames = min(len(df), 100)  # Limit to 100 frames for performance
        step = max(1, len(df) // frames)
        
        anim = FuncAnimation(fig, update, frames=range(1, len(df), step),
                             init_func=init, blit=True, interval=100)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save animation
        anim.save(output_path, writer='pillow', fps=10, dpi=100)
        plt.close()
        
        print(f"Animated time series saved to {output_path}")
    except Exception as e:
        print(f"Error creating animated time series: {e}")

def create_correlation_heatmap(df, output_path='visualizations/gas_fee_correlation.png'):
    """
    Create a correlation heatmap for gas fee and related metrics.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for correlation heatmap")
            return
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return
            
        # Extract relevant columns for correlation
        relevant_cols = [gas_fee_col]
        
        # Add other relevant columns if they exist
        for col in ['gas_used', 'gas_limit', 'tx_count', 'block_number']:
            if col in df.columns:
                relevant_cols.append(col)
                
        # Add time-based features
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            relevant_cols.extend(['hour', 'day_of_week'])
            
        # Calculate correlation matrix
        corr_matrix = df[relevant_cols].corr()
        
        # Create figure
        plt.figure(figsize=(12, 10))
        
        # Create heatmap
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap='coolwarm',
            vmin=-1,
            vmax=1,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={'shrink': 0.8, 'label': 'Correlation Coefficient'}
        )
        
        # Set title
        plt.title('Correlation Heatmap of Gas Fee and Related Metrics')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Correlation heatmap saved to {output_path}")
    except Exception as e:
        print(f"Error creating correlation heatmap: {e}")

def create_gas_fee_violin_plot(df, output_path='visualizations/gas_fee_violin.png'):
    """
    Create a violin plot of gas fees by day of week.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for violin plot")
            return
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            print("Timestamp column not found in data")
            return
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return
            
        # Extract day of week from timestamp
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Create violin plot
        sns.violinplot(
            x='day_of_week',
            y=gas_fee_col,
            data=df,
            order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            palette='viridis'
        )
        
        # Set labels and title
        plt.xlabel('Day of Week')
        plt.ylabel('Gas Fee (GWEI)')
        plt.title('Distribution of Gas Fees by Day of Week')
        
        # Add grid
        plt.grid(True, alpha=0.3, axis='y')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Violin plot saved to {output_path}")
    except Exception as e:
        print(f"Error creating violin plot: {e}")

def main():
    """Main function to run the advanced visualization pipeline."""
    try:
        # Load gas fee data
        df = load_gas_fee_data()
        
        if df is None:
            print("No gas fee data available. Generating sample data for demonstration.")
            
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
            
            # Add block data
            start_block = 17000000
            df['block_number'] = [start_block + i for i in range(len(df))]
            df['gas_used'] = np.random.randint(10000000, 30000000, size=len(df))
            df['gas_limit'] = 30000000
            df['tx_count'] = np.random.randint(50, 200, size=len(df))
            
            # Save sample data
            os.makedirs('data', exist_ok=True)
            df.to_csv('data/historical_gas_data.csv', index=False)
            print("Generated and saved sample gas fee data.")
        
        # Create advanced visualizations
        create_3d_surface_plot(df)
        create_animated_time_series(df)
        create_correlation_heatmap(df)
        create_gas_fee_violin_plot(df)
        
        print("All advanced visualizations completed successfully.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
