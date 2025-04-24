"""
Data Analysis for Ethereum Gas Fees

This script performs detailed analysis on Ethereum gas fee data to identify
patterns, trends, and anomalies. It generates statistical reports and insights
that can be used to optimize transaction timing and costs.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf

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

def generate_descriptive_statistics(df, output_path='data/gas_fee_statistics.csv'):
    """
    Generate descriptive statistics for gas fee data.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_path: Path to save the statistics
        
    Returns:
        DataFrame containing descriptive statistics
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for descriptive statistics")
            return None
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return None
            
        # Calculate overall statistics
        overall_stats = df[gas_fee_col].describe()
        
        # Calculate statistics by day of week
        if 'timestamp' in df.columns:
            df['day_of_week'] = df['timestamp'].dt.day_name()
            daily_stats = df.groupby('day_of_week')[gas_fee_col].describe()
            
            # Reorder days of week
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_stats = daily_stats.reindex(days_order)
            
        # Calculate statistics by hour
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            hourly_stats = df.groupby('hour')[gas_fee_col].describe()
            
        # Calculate additional statistics
        additional_stats = pd.Series({
            'skewness': stats.skew(df[gas_fee_col].dropna()),
            'kurtosis': stats.kurtosis(df[gas_fee_col].dropna()),
            'median_absolute_deviation': stats.median_abs_deviation(df[gas_fee_col].dropna()),
            'coefficient_of_variation': df[gas_fee_col].std() / df[gas_fee_col].mean() if df[gas_fee_col].mean() != 0 else np.nan
        })
        
        # Combine statistics
        all_stats = {
            'overall': overall_stats,
            'additional': additional_stats,
            'daily': daily_stats if 'day_of_week' in df.columns else None,
            'hourly': hourly_stats if 'hour' in df.columns else None
        }
        
        # Save statistics to CSV
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save overall and additional statistics
            pd.concat([overall_stats, additional_stats]).to_csv(output_path)
            
            # Save daily statistics
            if 'day_of_week' in df.columns:
                daily_stats.to_csv(output_path.replace('.csv', '_daily.csv'))
                
            # Save hourly statistics
            if 'hour' in df.columns:
                hourly_stats.to_csv(output_path.replace('.csv', '_hourly.csv'))
                
            print(f"Descriptive statistics saved to {output_path}")
            
        return all_stats
    except Exception as e:
        print(f"Error generating descriptive statistics: {e}")
        return None

def perform_time_series_analysis(df, output_dir='visualizations/time_series'):
    """
    Perform time series analysis on gas fee data.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_dir: Directory to save the visualizations
        
    Returns:
        Dictionary containing time series analysis results
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for time series analysis")
            return None
            
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            print("Timestamp column not found in data")
            return None
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return None
            
        # Sort data by timestamp
        df = df.sort_values('timestamp')
        
        # Set timestamp as index for time series analysis
        ts_df = df.set_index('timestamp')
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform seasonal decomposition
        try:
            # Resample to hourly frequency if needed
            if len(ts_df) > 24:
                ts_df_resampled = ts_df[gas_fee_col].resample('H').mean()
                
                # Fill missing values if any
                ts_df_resampled = ts_df_resampled.interpolate()
                
                # Perform decomposition
                decomposition = seasonal_decompose(ts_df_resampled, model='additive', period=24)
                
                # Plot decomposition
                fig, axes = plt.subplots(4, 1, figsize=(14, 12))
                
                decomposition.observed.plot(ax=axes[0])
                axes[0].set_title('Observed')
                axes[0].set_ylabel('Gas Fee (GWEI)')
                
                decomposition.trend.plot(ax=axes[1])
                axes[1].set_title('Trend')
                axes[1].set_ylabel('Gas Fee (GWEI)')
                
                decomposition.seasonal.plot(ax=axes[2])
                axes[2].set_title('Seasonal')
                axes[2].set_ylabel('Gas Fee (GWEI)')
                
                decomposition.resid.plot(ax=axes[3])
                axes[3].set_title('Residual')
                axes[3].set_ylabel('Gas Fee (GWEI)')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'seasonal_decomposition.png'), dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"Seasonal decomposition saved to {os.path.join(output_dir, 'seasonal_decomposition.png')}")
        except Exception as e:
            print(f"Error performing seasonal decomposition: {e}")
            
        # Perform autocorrelation analysis
        try:
            # Calculate ACF and PACF
            acf_values = acf(df[gas_fee_col].dropna(), nlags=48)
            pacf_values = pacf(df[gas_fee_col].dropna(), nlags=48)
            
            # Plot ACF and PACF
            fig, axes = plt.subplots(2, 1, figsize=(14, 10))
            
            # Plot ACF
            axes[0].stem(range(len(acf_values)), acf_values)
            axes[0].set_title('Autocorrelation Function (ACF)')
            axes[0].set_xlabel('Lag')
            axes[0].set_ylabel('Correlation')
            axes[0].axhline(y=0, linestyle='--', color='gray')
            axes[0].axhline(y=1.96/np.sqrt(len(df)), linestyle='--', color='red')
            axes[0].axhline(y=-1.96/np.sqrt(len(df)), linestyle='--', color='red')
            
            # Plot PACF
            axes[1].stem(range(len(pacf_values)), pacf_values)
            axes[1].set_title('Partial Autocorrelation Function (PACF)')
            axes[1].set_xlabel('Lag')
            axes[1].set_ylabel('Correlation')
            axes[1].axhline(y=0, linestyle='--', color='gray')
            axes[1].axhline(y=1.96/np.sqrt(len(df)), linestyle='--', color='red')
            axes[1].axhline(y=-1.96/np.sqrt(len(df)), linestyle='--', color='red')
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'autocorrelation.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Autocorrelation analysis saved to {os.path.join(output_dir, 'autocorrelation.png')}")
        except Exception as e:
            print(f"Error performing autocorrelation analysis: {e}")
            
        # Perform stationarity test
        try:
            # Perform Augmented Dickey-Fuller test
            adf_result = adfuller(df[gas_fee_col].dropna())
            
            adf_output = pd.Series({
                'Test Statistic': adf_result[0],
                'p-value': adf_result[1],
                'Critical Values (1%)': adf_result[4]['1%'],
                'Critical Values (5%)': adf_result[4]['5%'],
                'Critical Values (10%)': adf_result[4]['10%'],
                'Is Stationary': adf_result[1] < 0.05
            })
            
            # Save ADF test results
            adf_output.to_csv(os.path.join(output_dir, 'stationarity_test.csv'))
            print(f"Stationarity test results saved to {os.path.join(output_dir, 'stationarity_test.csv')}")
        except Exception as e:
            print(f"Error performing stationarity test: {e}")
            
        # Return analysis results
        return {
            'decomposition': decomposition if 'decomposition' in locals() else None,
            'acf': acf_values if 'acf_values' in locals() else None,
            'pacf': pacf_values if 'pacf_values' in locals() else None,
            'adf_test': adf_output if 'adf_output' in locals() else None
        }
    except Exception as e:
        print(f"Error performing time series analysis: {e}")
        return None

def analyze_gas_fee_anomalies(df, output_path='visualizations/gas_fee_anomalies.png'):
    """
    Analyze and visualize anomalies in gas fee data.
    
    Args:
        df: DataFrame containing historical gas fee data
        output_path: Path to save the visualization
        
    Returns:
        DataFrame containing detected anomalies
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for anomaly analysis")
            return None
            
        # Ensure gas fee column exists
        gas_fee_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                gas_fee_col = col
                break
                
        if gas_fee_col is None:
            print("Gas fee column not found in data")
            return None
            
        # Calculate z-scores
        df['z_score'] = stats.zscore(df[gas_fee_col])
        
        # Identify anomalies (z-score > 3 or z-score < -3)
        df['is_anomaly'] = (df['z_score'].abs() > 3)
        
        # Get anomalies
        anomalies = df[df['is_anomaly']]
        
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Plot gas fees
        plt.plot(df['timestamp'], df[gas_fee_col], label='Gas Fee')
        
        # Plot anomalies
        plt.scatter(
            anomalies['timestamp'],
            anomalies[gas_fee_col],
            color='red',
            label='Anomalies',
            s=50,
            zorder=5
        )
        
        # Set labels and title
        plt.xlabel('Time')
        plt.ylabel('Gas Fee (GWEI)')
        plt.title('Gas Fee Anomalies (Z-score > 3)')
        
        # Add legend
        plt.legend()
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Anomaly analysis visualization saved to {output_path}")
        
        # Save anomalies to CSV
        if len(anomalies) > 0:
            anomalies.to_csv(output_path.replace('.png', '.csv'), index=False)
            print(f"Anomalies saved to {output_path.replace('.png', '.csv')}")
            
        return anomalies
    except Exception as e:
        print(f"Error analyzing gas fee anomalies: {e}")
        return None

def main():
    """Main function to run the data analysis pipeline."""
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
            
            # Add some anomalies
            anomaly_indices = [24, 72, 120]  # Add anomalies at specific indices
            for idx in anomaly_indices:
                gas_fees[idx] = gas_fees[idx] * 2  # Double the gas fee to create an anomaly
            
            # Create sample DataFrame
            df = pd.DataFrame({
                'timestamp': timestamps,
                'base_fee_gwei': gas_fees
            })
            
            # Save sample data
            os.makedirs('data', exist_ok=True)
            df.to_csv('data/historical_gas_data.csv', index=False)
            print("Generated and saved sample gas fee data.")
        
        # Perform data analysis
        generate_descriptive_statistics(df)
        perform_time_series_analysis(df)
        analyze_gas_fee_anomalies(df)
        
        print("All data analysis completed successfully.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
