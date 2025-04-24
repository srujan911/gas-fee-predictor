"""
Advanced Features for Ethereum Gas Fee Predictor

This script implements advanced features for the Ethereum Gas Fee Predictor,
including confidence intervals, optimal transaction time recommendations,
and anomaly detection.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from scipy import stats

def load_prediction_data(file_path='data/gas_fee_predictions.csv'):
    """
    Load gas fee prediction data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing gas fee predictions
        
    Returns:
        DataFrame containing gas fee predictions
    """
    try:
        if not os.path.exists(file_path):
            print(f"Warning: Prediction data file not found at {file_path}")
            return None
            
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime if it's not already
        if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        print(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading prediction data: {e}")
        return None

def calculate_confidence_intervals(df, target_col=None, prediction_col='predicted_fee', confidence=0.95):
    """
    Calculate confidence intervals for gas fee predictions.
    
    Args:
        df: DataFrame containing gas fee predictions
        target_col: Column name for actual gas fee (if None, will try to detect)
        prediction_col: Column name for predicted gas fee
        confidence: Confidence level (default: 0.95 for 95% confidence)
        
    Returns:
        DataFrame with confidence intervals added
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for confidence interval calculation")
            return None
            
        # Ensure prediction column exists
        if prediction_col not in df.columns:
            print(f"Prediction column '{prediction_col}' not found in data")
            return None
            
        # Ensure target column exists
        if target_col is None:
            for col in ['gas_fee', 'base_fee_gwei']:
                if col in df.columns:
                    target_col = col
                    break
                    
        if target_col is None:
            print("Target column not found in data")
            return None
            
        # Make a copy of the DataFrame
        result_df = df.copy()
        
        # Calculate prediction errors
        if 'prediction_error' not in result_df.columns:
            result_df['prediction_error'] = result_df[target_col] - result_df[prediction_col]
            
        # Calculate standard deviation of prediction errors
        error_std = result_df['prediction_error'].std()
        
        # Calculate z-score for the given confidence level
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        # Calculate confidence interval
        margin = z_score * error_std
        
        # Add confidence interval bounds
        result_df['lower_bound'] = result_df[prediction_col] - margin
        result_df['upper_bound'] = result_df[prediction_col] + margin
        
        # Ensure lower bound is not negative
        result_df['lower_bound'] = result_df['lower_bound'].clip(lower=0)
        
        # Add confidence level information
        result_df['confidence_level'] = confidence
        result_df['confidence_margin'] = margin
        
        print(f"Calculated {confidence*100}% confidence intervals with margin ±{margin:.4f} GWEI")
        return result_df
    except Exception as e:
        print(f"Error calculating confidence intervals: {e}")
        return None

def detect_anomalies(df, target_col=None, contamination=0.05):
    """
    Detect anomalies in gas fee data using Isolation Forest.
    
    Args:
        df: DataFrame containing gas fee data
        target_col: Column name for gas fee (if None, will try to detect)
        contamination: Expected proportion of anomalies (default: 0.05)
        
    Returns:
        DataFrame with anomaly flags added
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for anomaly detection")
            return None
            
        # Ensure target column exists
        if target_col is None:
            for col in ['gas_fee', 'base_fee_gwei']:
                if col in df.columns:
                    target_col = col
                    break
                    
        if target_col is None:
            print("Target column not found in data")
            return None
            
        # Make a copy of the DataFrame
        result_df = df.copy()
        
        # Extract features for anomaly detection
        features = [target_col]
        
        # Add time-based features if available
        if 'hour' in result_df.columns:
            features.append('hour')
            
        if 'day_of_week' in result_df.columns:
            features.append('day_of_week')
            
        # Add prediction-based features if available
        if 'predicted_fee' in result_df.columns:
            features.append('predicted_fee')
            
        if 'prediction_error' in result_df.columns:
            features.append('prediction_error')
            
        # Initialize Isolation Forest
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        # Fit and predict
        result_df['anomaly'] = iso_forest.fit_predict(result_df[features])
        
        # Convert to binary flag (1 for anomaly, 0 for normal)
        result_df['anomaly'] = (result_df['anomaly'] == -1).astype(int)
        
        # Calculate anomaly score (higher score = more anomalous)
        result_df['anomaly_score'] = iso_forest.decision_function(result_df[features]) * -1
        
        # Count anomalies
        anomaly_count = result_df['anomaly'].sum()
        
        print(f"Detected {anomaly_count} anomalies ({anomaly_count/len(result_df)*100:.2f}% of data)")
        return result_df
    except Exception as e:
        print(f"Error detecting anomalies: {e}")
        return None

def find_optimal_transaction_times(df, target_col=None, group_by='hour', top_n=5):
    """
    Find optimal times for transactions based on gas fee patterns.
    
    Args:
        df: DataFrame containing gas fee data
        target_col: Column name for gas fee (if None, will try to detect)
        group_by: Column to group by ('hour', 'day_of_week', or 'both')
        top_n: Number of optimal times to return
        
    Returns:
        DataFrame containing optimal transaction times
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for finding optimal transaction times")
            return None
            
        # Ensure target column exists
        if target_col is None:
            for col in ['gas_fee', 'base_fee_gwei']:
                if col in df.columns:
                    target_col = col
                    break
                    
        if target_col is None:
            print("Target column not found in data")
            return None
            
        # Make a copy of the DataFrame
        result_df = df.copy()
        
        # Ensure time columns exist
        if 'timestamp' in result_df.columns:
            if 'hour' not in result_df.columns:
                result_df['hour'] = result_df['timestamp'].dt.hour
                
            if 'day_of_week' not in result_df.columns:
                result_df['day_of_week'] = result_df['timestamp'].dt.dayofweek
                result_df['day_name'] = result_df['timestamp'].dt.day_name()
        else:
            print("Timestamp column not found in data")
            return None
            
        # Group by specified column(s)
        if group_by == 'hour':
            grouped = result_df.groupby('hour')[target_col].agg(['mean', 'std', 'count']).reset_index()
            grouped['time_group'] = grouped['hour'].apply(lambda x: f"{x:02d}:00")
        elif group_by == 'day_of_week':
            grouped = result_df.groupby(['day_of_week', 'day_name'])[target_col].agg(['mean', 'std', 'count']).reset_index()
            grouped['time_group'] = grouped['day_name']
        elif group_by == 'both':
            grouped = result_df.groupby(['day_of_week', 'day_name', 'hour'])[target_col].agg(['mean', 'std', 'count']).reset_index()
            grouped['time_group'] = grouped.apply(lambda x: f"{x['day_name']} at {x['hour']:02d}:00", axis=1)
        else:
            print(f"Invalid group_by value: {group_by}")
            return None
            
        # Calculate coefficient of variation (lower is more reliable)
        grouped['cv'] = grouped['std'] / grouped['mean']
        
        # Calculate reliability score (inverse of CV, higher is more reliable)
        grouped['reliability'] = 1 - grouped['cv']
        grouped['reliability'] = grouped['reliability'].clip(lower=0)  # Ensure non-negative
        
        # Sort by mean gas fee (ascending) and reliability (descending)
        optimal_times = grouped.sort_values(['mean', 'reliability'], ascending=[True, False]).head(top_n)
        
        print(f"Found {len(optimal_times)} optimal transaction times")
        return optimal_times
    except Exception as e:
        print(f"Error finding optimal transaction times: {e}")
        return None

def generate_transaction_recommendations(df, amount_gwei=None, transaction_type='simple'):
    """
    Generate transaction recommendations based on gas fee predictions.
    
    Args:
        df: DataFrame containing gas fee predictions
        amount_gwei: Transaction amount in GWEI (optional)
        transaction_type: Type of transaction ('simple', 'token', 'swap', 'nft', 'complex')
        
    Returns:
        Dictionary containing transaction recommendations
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for transaction recommendations")
            return None
            
        # Ensure prediction column exists
        if 'predicted_fee' not in df.columns:
            print("Predicted fee column not found in data")
            return None
            
        # Define gas limits for different transaction types
        gas_limits = {
            'simple': 21000,
            'token': 65000,
            'swap': 150000,
            'nft': 200000,
            'complex': 300000
        }
        
        # Get gas limit for the specified transaction type
        gas_limit = gas_limits.get(transaction_type, 21000)
        
        # Get current gas fee (most recent prediction)
        if 'timestamp' in df.columns:
            current_row = df.sort_values('timestamp', ascending=False).iloc[0]
        else:
            current_row = df.iloc[-1]
            
        current_fee = current_row['predicted_fee']
        
        # Get optimal transaction times
        optimal_times = find_optimal_transaction_times(df)
        
        if optimal_times is None or len(optimal_times) == 0:
            print("Failed to find optimal transaction times")
            return None
            
        # Get lowest gas fee time
        lowest_fee_time = optimal_times.iloc[0]
        lowest_fee = lowest_fee_time['mean']
        
        # Calculate potential savings
        savings_gwei = current_fee - lowest_fee
        savings_percent = (savings_gwei / current_fee) * 100 if current_fee > 0 else 0
        
        # Calculate transaction cost
        eth_per_gwei = 0.000000001  # 1 GWEI = 10^-9 ETH
        
        current_cost_eth = current_fee * gas_limit * eth_per_gwei
        lowest_cost_eth = lowest_fee * gas_limit * eth_per_gwei
        
        # Assume ETH price in USD (could be fetched from an API in a real implementation)
        eth_price_usd = 3000
        
        current_cost_usd = current_cost_eth * eth_price_usd
        lowest_cost_usd = lowest_cost_eth * eth_price_usd
        
        # Generate recommendations
        recommendations = {
            'transaction_type': transaction_type,
            'gas_limit': gas_limit,
            'current_fee': {
                'gwei': current_fee,
                'cost_eth': current_cost_eth,
                'cost_usd': current_cost_usd
            },
            'optimal_time': {
                'time_group': lowest_fee_time['time_group'],
                'fee_gwei': lowest_fee,
                'cost_eth': lowest_cost_eth,
                'cost_usd': lowest_cost_usd,
                'reliability': lowest_fee_time['reliability']
            },
            'potential_savings': {
                'gwei': savings_gwei,
                'percent': savings_percent,
                'eth': current_cost_eth - lowest_cost_eth,
                'usd': current_cost_usd - lowest_cost_usd
            },
            'all_optimal_times': optimal_times[['time_group', 'mean', 'reliability']].rename(
                columns={'mean': 'fee_gwei'}
            ).to_dict('records')
        }
        
        print(f"Generated transaction recommendations for {transaction_type} transaction")
        return recommendations
    except Exception as e:
        print(f"Error generating transaction recommendations: {e}")
        return None

def visualize_confidence_intervals(df, output_path='visualizations/confidence_intervals.png'):
    """
    Visualize gas fee predictions with confidence intervals.
    
    Args:
        df: DataFrame containing gas fee predictions with confidence intervals
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for visualization")
            return
            
        # Ensure required columns exist
        required_cols = ['timestamp', 'predicted_fee', 'lower_bound', 'upper_bound']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"Missing required columns for visualization: {missing_cols}")
            return
            
        # Ensure target column exists
        target_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                target_col = col
                break
                
        if target_col is None:
            print("Target column not found in data")
            return
            
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Plot actual values
        plt.plot(df['timestamp'], df[target_col], label='Actual', color='black', linewidth=2)
        
        # Plot predicted values
        plt.plot(df['timestamp'], df['predicted_fee'], label='Predicted', color='blue', linewidth=2)
        
        # Plot confidence intervals
        plt.fill_between(
            df['timestamp'],
            df['lower_bound'],
            df['upper_bound'],
            alpha=0.2,
            color='blue',
            label=f"{df['confidence_level'].iloc[0]*100:.0f}% Confidence Interval"
        )
        
        # Set labels and title
        plt.xlabel('Time')
        plt.ylabel('Gas Fee (GWEI)')
        plt.title('Gas Fee Predictions with Confidence Intervals')
        
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
        
        print(f"Confidence interval visualization saved to {output_path}")
    except Exception as e:
        print(f"Error visualizing confidence intervals: {e}")

def visualize_optimal_times(df, output_path='visualizations/optimal_times.png'):
    """
    Visualize optimal transaction times.
    
    Args:
        df: DataFrame containing gas fee data
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for visualization")
            return
            
        # Find optimal transaction times
        optimal_times = find_optimal_transaction_times(df, group_by='both', top_n=10)
        
        if optimal_times is None or len(optimal_times) == 0:
            print("Failed to find optimal transaction times")
            return
            
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Plot optimal times
        sns.barplot(
            x='time_group',
            y='mean',
            data=optimal_times,
            palette='viridis'
        )
        
        # Set labels and title
        plt.xlabel('Time')
        plt.ylabel('Average Gas Fee (GWEI)')
        plt.title('Optimal Transaction Times by Average Gas Fee')
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        plt.grid(True, alpha=0.3, axis='y')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Optimal times visualization saved to {output_path}")
    except Exception as e:
        print(f"Error visualizing optimal times: {e}")

def visualize_anomalies(df, output_path='visualizations/anomalies.png'):
    """
    Visualize anomalies in gas fee data.
    
    Args:
        df: DataFrame containing gas fee data with anomaly flags
        output_path: Path to save the visualization
        
    Returns:
        None
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for visualization")
            return
            
        # Ensure required columns exist
        if 'anomaly' not in df.columns:
            print("Anomaly column not found in data")
            return
            
        # Ensure target column exists
        target_col = None
        for col in ['gas_fee', 'base_fee_gwei']:
            if col in df.columns:
                target_col = col
                break
                
        if target_col is None:
            print("Target column not found in data")
            return
            
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Plot normal points
        normal_df = df[df['anomaly'] == 0]
        plt.scatter(
            normal_df['timestamp'],
            normal_df[target_col],
            label='Normal',
            color='blue',
            alpha=0.5
        )
        
        # Plot anomalies
        anomaly_df = df[df['anomaly'] == 1]
        plt.scatter(
            anomaly_df['timestamp'],
            anomaly_df[target_col],
            label='Anomaly',
            color='red',
            s=100,
            marker='x'
        )
        
        # Set labels and title
        plt.xlabel('Time')
        plt.ylabel('Gas Fee (GWEI)')
        plt.title('Gas Fee Anomalies')
        
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
        
        print(f"Anomaly visualization saved to {output_path}")
    except Exception as e:
        print(f"Error visualizing anomalies: {e}")

def main():
    """Main function to run the advanced features pipeline."""
    try:
        # Load prediction data
        df = load_prediction_data()
        
        if df is None:
            print("No prediction data available. Please run add_predictions_to_csv.py first.")
            return
            
        # Calculate confidence intervals
        df_with_ci = calculate_confidence_intervals(df)
        
        if df_with_ci is not None:
            # Visualize confidence intervals
            visualize_confidence_intervals(df_with_ci)
            
        # Detect anomalies
        df_with_anomalies = detect_anomalies(df)
        
        if df_with_anomalies is not None:
            # Visualize anomalies
            visualize_anomalies(df_with_anomalies)
            
        # Find optimal transaction times
        optimal_times = find_optimal_transaction_times(df)
        
        if optimal_times is not None:
            # Visualize optimal times
            visualize_optimal_times(df)
            
        # Generate transaction recommendations
        for tx_type in ['simple', 'token', 'swap', 'nft', 'complex']:
            recommendations = generate_transaction_recommendations(df, transaction_type=tx_type)
            
            if recommendations is not None:
                # Print recommendations
                print(f"\nRecommendations for {tx_type} transaction:")
                print(f"Current fee: {recommendations['current_fee']['gwei']:.4f} GWEI (${recommendations['current_fee']['cost_usd']:.4f})")
                print(f"Optimal time: {recommendations['optimal_time']['time_group']} at {recommendations['optimal_time']['fee_gwei']:.4f} GWEI (${recommendations['optimal_time']['cost_usd']:.4f})")
                print(f"Potential savings: {recommendations['potential_savings']['gwei']:.4f} GWEI ({recommendations['potential_savings']['percent']:.2f}%, ${recommendations['potential_savings']['usd']:.4f})")
                
        print("\nAdvanced features processing completed successfully.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
