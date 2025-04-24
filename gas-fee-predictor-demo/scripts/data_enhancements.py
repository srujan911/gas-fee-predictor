"""
Data Enhancements for Ethereum Gas Fee Analysis

This script enhances the Ethereum gas fee data by adding additional features
and metrics that can improve analysis and prediction accuracy.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from sklearn.preprocessing import StandardScaler, MinMaxScaler

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

def add_time_features(df):
    """
    Add time-based features to the DataFrame.
    
    Args:
        df: DataFrame containing gas fee data with timestamp column
        
    Returns:
        DataFrame with added time features
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for adding time features")
            return df
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            print("Timestamp column not found in data")
            return df
            
        # Make a copy to avoid modifying the original DataFrame
        enhanced_df = df.copy()
        
        # Extract basic time features
        enhanced_df['hour'] = enhanced_df['timestamp'].dt.hour
        enhanced_df['day_of_week'] = enhanced_df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        enhanced_df['day_name'] = enhanced_df['timestamp'].dt.day_name()
        enhanced_df['month'] = enhanced_df['timestamp'].dt.month
        enhanced_df['year'] = enhanced_df['timestamp'].dt.year
        enhanced_df['quarter'] = enhanced_df['timestamp'].dt.quarter
        
        # Add cyclical features for hour and day of week
        enhanced_df['hour_sin'] = np.sin(2 * np.pi * enhanced_df['hour'] / 24)
        enhanced_df['hour_cos'] = np.cos(2 * np.pi * enhanced_df['hour'] / 24)
        enhanced_df['day_sin'] = np.sin(2 * np.pi * enhanced_df['day_of_week'] / 7)
        enhanced_df['day_cos'] = np.cos(2 * np.pi * enhanced_df['day_of_week'] / 7)
        
        # Add is_weekend feature
        enhanced_df['is_weekend'] = enhanced_df['day_of_week'].isin([5, 6]).astype(int)
        
        # Add time of day category
        conditions = [
            (enhanced_df['hour'] >= 0) & (enhanced_df['hour'] < 6),
            (enhanced_df['hour'] >= 6) & (enhanced_df['hour'] < 12),
            (enhanced_df['hour'] >= 12) & (enhanced_df['hour'] < 18),
            (enhanced_df['hour'] >= 18) & (enhanced_df['hour'] < 24)
        ]
        categories = ['night', 'morning', 'afternoon', 'evening']
        enhanced_df['time_of_day'] = np.select(conditions, categories, default='unknown')
        
        print("Added time features to DataFrame")
        return enhanced_df
    except Exception as e:
        print(f"Error adding time features: {e}")
        return df

def add_rolling_statistics(df, gas_fee_col=None, windows=[1, 6, 12, 24]):
    """
    Add rolling statistics for gas fees.
    
    Args:
        df: DataFrame containing gas fee data
        gas_fee_col: Column name for gas fee data (if None, will try to detect)
        windows: List of window sizes for rolling statistics
        
    Returns:
        DataFrame with added rolling statistics
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for adding rolling statistics")
            return df
            
        # Ensure gas fee column exists
        if gas_fee_col is None:
            for col in ['gas_fee', 'base_fee_gwei']:
                if col in df.columns:
                    gas_fee_col = col
                    break
                    
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return df
            
        # Make a copy to avoid modifying the original DataFrame
        enhanced_df = df.copy()
        
        # Ensure data is sorted by timestamp
        if 'timestamp' in enhanced_df.columns:
            enhanced_df = enhanced_df.sort_values('timestamp')
            
        # Add rolling statistics for each window size
        for window in windows:
            # Add rolling mean
            enhanced_df[f'{gas_fee_col}_rolling_mean_{window}'] = enhanced_df[gas_fee_col].rolling(window=window).mean()
            
            # Add rolling standard deviation
            enhanced_df[f'{gas_fee_col}_rolling_std_{window}'] = enhanced_df[gas_fee_col].rolling(window=window).std()
            
            # Add rolling min and max
            enhanced_df[f'{gas_fee_col}_rolling_min_{window}'] = enhanced_df[gas_fee_col].rolling(window=window).min()
            enhanced_df[f'{gas_fee_col}_rolling_max_{window}'] = enhanced_df[gas_fee_col].rolling(window=window).max()
            
            # Add rolling median
            enhanced_df[f'{gas_fee_col}_rolling_median_{window}'] = enhanced_df[gas_fee_col].rolling(window=window).median()
            
        # Add percentage change features
        enhanced_df[f'{gas_fee_col}_pct_change_1'] = enhanced_df[gas_fee_col].pct_change()
        enhanced_df[f'{gas_fee_col}_pct_change_24'] = enhanced_df[gas_fee_col].pct_change(periods=24)
        
        # Add difference features
        enhanced_df[f'{gas_fee_col}_diff_1'] = enhanced_df[gas_fee_col].diff()
        enhanced_df[f'{gas_fee_col}_diff_24'] = enhanced_df[gas_fee_col].diff(periods=24)
        
        print("Added rolling statistics to DataFrame")
        return enhanced_df
    except Exception as e:
        print(f"Error adding rolling statistics: {e}")
        return df

def add_block_features(df):
    """
    Add block-related features to the DataFrame.
    
    Args:
        df: DataFrame containing gas fee data with block information
        
    Returns:
        DataFrame with added block features
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for adding block features")
            return df
            
        # Check if required columns exist
        required_cols = ['gas_used', 'gas_limit', 'tx_count']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"Missing required columns for block features: {missing_cols}")
            return df
            
        # Make a copy to avoid modifying the original DataFrame
        enhanced_df = df.copy()
        
        # Add block utilization percentage
        enhanced_df['block_utilization'] = (enhanced_df['gas_used'] / enhanced_df['gas_limit']) * 100
        
        # Add gas per transaction
        enhanced_df['gas_per_tx'] = enhanced_df['gas_used'] / enhanced_df['tx_count'].replace(0, np.nan)
        
        # Add block efficiency (gas used per transaction relative to limit)
        enhanced_df['block_efficiency'] = (enhanced_df['gas_used'] / enhanced_df['tx_count'].replace(0, np.nan)) / enhanced_df['gas_limit']
        
        # Add block congestion indicator (1 if utilization > 80%, 0 otherwise)
        enhanced_df['block_congestion'] = (enhanced_df['block_utilization'] > 80).astype(int)
        
        print("Added block features to DataFrame")
        return enhanced_df
    except Exception as e:
        print(f"Error adding block features: {e}")
        return df

def add_market_data(df, api_key=None):
    """
    Add Ethereum market data to the DataFrame.
    
    Args:
        df: DataFrame containing gas fee data with timestamp column
        api_key: API key for market data provider (optional)
        
    Returns:
        DataFrame with added market data
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for adding market data")
            return df
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            print("Timestamp column not found in data")
            return df
            
        # Make a copy to avoid modifying the original DataFrame
        enhanced_df = df.copy()
        
        # Get date range
        start_date = enhanced_df['timestamp'].min().strftime('%Y-%m-%d')
        end_date = enhanced_df['timestamp'].max().strftime('%Y-%m-%d')
        
        # Try to fetch market data from API
        try:
            if api_key:
                # Example API call (replace with actual API)
                url = f"https://api.example.com/ethereum/historical?start={start_date}&end={end_date}&apikey={api_key}"
                response = requests.get(url)
                market_data = response.json()
                
                # Create DataFrame from API response
                market_df = pd.DataFrame(market_data)
                market_df['timestamp'] = pd.to_datetime(market_df['timestamp'])
                
                # Merge with enhanced_df
                enhanced_df = pd.merge_asof(
                    enhanced_df.sort_values('timestamp'),
                    market_df.sort_values('timestamp'),
                    on='timestamp',
                    direction='nearest'
                )
                
                print("Added market data from API")
            else:
                # Generate synthetic market data for demonstration
                print("No API key provided. Generating synthetic market data.")
                
                # Get unique dates
                dates = enhanced_df['timestamp'].dt.floor('D').unique()
                
                # Generate synthetic price data
                np.random.seed(42)
                base_price = 3000  # Base ETH price in USD
                price_data = []
                
                for date in dates:
                    # Generate daily price with some randomness
                    daily_price = base_price * (1 + np.random.normal(0, 0.02))  # 2% daily volatility
                    
                    # Add hourly prices
                    for hour in range(24):
                        timestamp = date + pd.Timedelta(hours=hour)
                        hourly_price = daily_price * (1 + np.random.normal(0, 0.005))  # 0.5% hourly volatility
                        volume = np.random.randint(1000, 10000)
                        
                        price_data.append({
                            'timestamp': timestamp,
                            'eth_price_usd': hourly_price,
                            'eth_volume': volume,
                            'market_cap': hourly_price * 120000000  # Assuming 120M ETH supply
                        })
                
                # Create market DataFrame
                market_df = pd.DataFrame(price_data)
                
                # Merge with enhanced_df
                enhanced_df = pd.merge_asof(
                    enhanced_df.sort_values('timestamp'),
                    market_df.sort_values('timestamp'),
                    on='timestamp',
                    direction='nearest'
                )
                
                print("Added synthetic market data")
        except Exception as e:
            print(f"Error fetching market data: {e}")
            print("Continuing without market data")
            
        return enhanced_df
    except Exception as e:
        print(f"Error adding market data: {e}")
        return df

def normalize_features(df, exclude_cols=None):
    """
    Normalize numerical features in the DataFrame.
    
    Args:
        df: DataFrame containing features to normalize
        exclude_cols: List of columns to exclude from normalization
        
    Returns:
        DataFrame with normalized features
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for normalization")
            return df
            
        # Make a copy to avoid modifying the original DataFrame
        normalized_df = df.copy()
        
        # Default exclude columns
        if exclude_cols is None:
            exclude_cols = ['timestamp', 'block_number', 'day_name', 'time_of_day']
            
        # Add any categorical columns to exclude list
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                exclude_cols.append(col)
                
        # Get columns to normalize
        normalize_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Initialize scaler
        scaler = StandardScaler()
        
        # Normalize features
        normalized_df[normalize_cols] = scaler.fit_transform(df[normalize_cols].fillna(0))
        
        print(f"Normalized {len(normalize_cols)} features")
        return normalized_df
    except Exception as e:
        print(f"Error normalizing features: {e}")
        return df

def save_enhanced_data(df, output_path='data/enhanced_gas_data.csv'):
    """
    Save enhanced gas fee data to CSV file.
    
    Args:
        df: DataFrame containing enhanced gas fee data
        output_path: Path to save the enhanced data
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available to save")
            return
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        
        print(f"Enhanced data saved to {output_path}")
    except Exception as e:
        print(f"Error saving enhanced data: {e}")

def main():
    """Main function to run the data enhancement pipeline."""
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
        
        # Apply enhancements
        enhanced_df = df.copy()
        enhanced_df = add_time_features(enhanced_df)
        enhanced_df = add_rolling_statistics(enhanced_df)
        enhanced_df = add_block_features(enhanced_df)
        enhanced_df = add_market_data(enhanced_df)
        
        # Save enhanced data
        save_enhanced_data(enhanced_df)
        
        # Create normalized version
        normalized_df = normalize_features(enhanced_df)
        save_enhanced_data(normalized_df, output_path='data/normalized_gas_data.csv')
        
        print("All data enhancements completed successfully.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
