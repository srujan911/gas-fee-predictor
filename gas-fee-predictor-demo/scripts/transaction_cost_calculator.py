#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Transaction Cost Calculator

This script calculates and visualizes the cost of different types of Ethereum
transactions based on current and predicted gas fees.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import joblib
from web3 import Web3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define transaction types and their typical gas usage
TRANSACTION_TYPES = {
    "ETH Transfer": 21000,
    "ERC-20 Transfer": 65000,
    "Uniswap Swap": 180000,
    "NFT Mint": 150000,
    "NFT Transfer": 60000,
    "DAO Vote": 80000,
    "Lending Deposit": 110000,
    "Lending Withdraw": 95000,
    "Simple Contract Deploy": 200000,
    "Complex Contract Deploy": 1000000
}

def load_model(model_path="models/gas_fee_model.pkl"):
    """Load the trained model and scaler."""
    try:
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        logger.info(f"Loading model from {model_path}")
        model_data = joblib.load(model_path)
        
        # Check if the model is a tuple (model, scaler)
        if isinstance(model_data, tuple) and len(model_data) == 2:
            model, scaler = model_data
            logger.info("Model and scaler loaded successfully")
            return model, scaler
        else:
            logger.error("Invalid model format: expected (model, scaler) tuple")
            raise ValueError("Invalid model format: expected (model, scaler) tuple")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def connect_to_ethereum():
    """Connect to the Ethereum network."""
    try:
        # Load environment variables
        infura_url = os.getenv("ETHEREUM_NODE_URL", 
                              "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b")
        
        logger.info(f"Connecting to Ethereum node")
        web3 = Web3(Web3.HTTPProvider(infura_url))
        
        if not web3.is_connected():
            logger.error("Failed to connect to Ethereum")
            raise ConnectionError("Not connected to Ethereum")
            
        logger.info(f"Connected to Ethereum network. Chain ID: {web3.eth.chain_id}")
        return web3
    except Exception as e:
        logger.error(f"Error connecting to Ethereum: {e}")
        raise

def get_current_gas_fee(web3):
    """Get the current gas fee from the Ethereum network."""
    try:
        logger.info("Fetching current gas fee")
        block = web3.eth.get_block("latest")
        base_fee = float(block.get("baseFeePerGas", 0)) / 1e9  # Convert to GWEI
        
        logger.info(f"Current base fee: {base_fee:.2f} GWEI")
        return base_fee
    except Exception as e:
        logger.error(f"Error fetching current gas fee: {e}")
        raise

def get_eth_price():
    """Get the current ETH price in USD."""
    try:
        # In a real implementation, this would call a price API
        # For demonstration, we'll use a fixed price
        eth_price = 3500.00
        logger.info(f"Current ETH price: ${eth_price:.2f}")
        return eth_price
    except Exception as e:
        logger.error(f"Error fetching ETH price: {e}")
        return 3500.00  # Default fallback price

def calculate_transaction_costs(gas_fee, eth_price):
    """Calculate the cost of different transaction types."""
    try:
        logger.info("Calculating transaction costs")
        
        results = []
        for tx_type, gas_used in TRANSACTION_TYPES.items():
            # Calculate costs
            cost_in_gwei = gas_used * gas_fee
            cost_in_eth = cost_in_gwei / 1e9
            cost_in_usd = cost_in_eth * eth_price
            
            results.append({
                "transaction_type": tx_type,
                "gas_used": gas_used,
                "cost_in_gwei": cost_in_gwei,
                "cost_in_eth": cost_in_eth,
                "cost_in_usd": cost_in_usd
            })
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(results)
        logger.info(f"Calculated costs for {len(df)} transaction types")
        return df
    except Exception as e:
        logger.error(f"Error calculating transaction costs: {e}")
        raise

def visualize_transaction_costs(costs_df, gas_fee, eth_price, output_path="visualizations/transaction_costs.png"):
    """Visualize transaction costs."""
    try:
        logger.info("Creating transaction cost visualization")
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
        
        # Sort by cost
        costs_df = costs_df.sort_values("cost_in_usd")
        
        # 1. Bar chart of USD costs
        bars = ax1.barh(costs_df["transaction_type"], costs_df["cost_in_usd"], color="green")
        
        # Add cost labels
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f"${width:.2f}", va="center")
        
        # Add labels and title
        ax1.set_xlabel("Cost (USD)", fontsize=12)
        ax1.set_title("Transaction Costs in USD", fontsize=16)
        ax1.grid(True, axis="x", alpha=0.3)
        
        # 2. Bar chart of ETH costs
        bars = ax2.barh(costs_df["transaction_type"], costs_df["cost_in_eth"], color="blue")
        
        # Add cost labels
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 0.0001, bar.get_y() + bar.get_height()/2, 
                   f"{width:.6f} ETH", va="center")
        
        # Add labels and title
        ax2.set_xlabel("Cost (ETH)", fontsize=12)
        ax2.set_title("Transaction Costs in ETH", fontsize=16)
        ax2.grid(True, axis="x", alpha=0.3)
        
        # Add overall title
        plt.suptitle(f"Ethereum Transaction Costs at {gas_fee:.2f} GWEI (ETH: ${eth_price:.2f})", 
                    fontsize=20, y=0.98)
        
        # Add timestamp
        plt.figtext(0.5, 0.01, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   ha="center", fontsize=10, style='italic')
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the visualization
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Transaction cost visualization saved to {output_path}")
        
        return output_path
    except Exception as e:
        logger.error(f"Error visualizing transaction costs: {e}")
        raise

def create_cost_comparison_chart(current_fee, predicted_fee, eth_price, 
                               output_path="visualizations/cost_comparison.png"):
    """Create a chart comparing costs with current vs predicted fees."""
    try:
        logger.info("Creating cost comparison chart")
        
        # Calculate costs for both fee levels
        current_costs = calculate_transaction_costs(current_fee, eth_price)
        predicted_costs = calculate_transaction_costs(predicted_fee, eth_price)
        
        # Create figure
        plt.figure(figsize=(14, 10))
        
        # Select a subset of transaction types for clarity
        selected_types = ["ETH Transfer", "ERC-20 Transfer", "Uniswap Swap", "NFT Mint", "DAO Vote"]
        
        # Filter and sort data
        current_subset = current_costs[current_costs["transaction_type"].isin(selected_types)]
        predicted_subset = predicted_costs[predicted_costs["transaction_type"].isin(selected_types)]
        
        # Sort by current cost
        current_subset = current_subset.sort_values("cost_in_usd")
        
        # Get transaction types in sorted order
        tx_types = current_subset["transaction_type"].tolist()
        
        # Reindex predicted costs to match order
        predicted_subset = predicted_subset.set_index("transaction_type").reindex(tx_types).reset_index()
        
        # Set up bar positions
        x = np.arange(len(tx_types))
        width = 0.35
        
        # Create grouped bar chart
        ax = plt.gca()
        current_bars = ax.bar(x - width/2, current_subset["cost_in_usd"], width, 
                             label=f"Current ({current_fee:.2f} GWEI)", color="blue")
        predicted_bars = ax.bar(x + width/2, predicted_subset["cost_in_usd"], width,
                               label=f"Predicted ({predicted_fee:.2f} GWEI)", color="red")
        
        # Add cost labels
        for bars in [current_bars, predicted_bars]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                       f"${height:.2f}", ha="center", va="bottom", fontsize=9)
        
        # Add labels and title
        ax.set_xlabel("Transaction Type", fontsize=12)
        ax.set_ylabel("Cost (USD)", fontsize=12)
        ax.set_title("Transaction Cost Comparison: Current vs Predicted Gas Fee", fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(tx_types, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)
        
        # Add savings information
        total_current = current_subset["cost_in_usd"].sum()
        total_predicted = predicted_subset["cost_in_usd"].sum()
        savings = total_current - total_predicted
        savings_percent = (savings / total_current) * 100 if total_current > 0 else 0
        
        if savings > 0:
            savings_text = f"Potential Savings: ${savings:.2f} ({savings_percent:.1f}%)"
            color = "green"
        else:
            savings_text = f"Potential Increase: ${-savings:.2f} ({-savings_percent:.1f}%)"
            color = "red"
        
        plt.figtext(0.5, 0.01, savings_text, ha="center", fontsize=14, 
                   fontweight="bold", color=color)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the chart
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Cost comparison chart saved to {output_path}")
        
        return output_path
    except Exception as e:
        logger.error(f"Error creating cost comparison chart: {e}")
        raise

def display_results(current_fee, predicted_fee, eth_price, costs_path, comparison_path):
    """Display the results of the transaction cost calculation."""
    print("\n" + "=" * 60)
    print("💰 ETHEREUM TRANSACTION COST CALCULATOR 💰")
    print("=" * 60)
    print(f"Current Gas Fee: {current_fee:.2f} GWEI")
    print(f"Predicted Gas Fee: {predicted_fee:.2f} GWEI")
    print(f"ETH Price: ${eth_price:.2f}")
    
    # Calculate difference
    diff = predicted_fee - current_fee
    percent = (diff / current_fee) * 100 if current_fee > 0 else 0
    
    if diff > 0:
        print(f"Gas Fee Trend: 🔴 Increasing by {diff:.2f} GWEI ({percent:.1f}%)")
    elif diff < 0:
        print(f"Gas Fee Trend: 🟢 Decreasing by {-diff:.2f} GWEI ({-percent:.1f}%)")
    else:
        print(f"Gas Fee Trend: ⚪ Stable (0% change)")
    
    print("\n📊 TRANSACTION COST VISUALIZATIONS:")
    print(f"  • Current Costs Chart: {costs_path}")
    print(f"  • Cost Comparison Chart: {comparison_path}")
    
    print("\n💡 SAMPLE TRANSACTION COSTS:")
    
    # Calculate costs for sample transactions
    costs_df = calculate_transaction_costs(current_fee, eth_price)
    for tx_type in ["ETH Transfer", "ERC-20 Transfer", "Uniswap Swap"]:
        row = costs_df[costs_df["transaction_type"] == tx_type].iloc[0]
        print(f"  • {tx_type}: ${row['cost_in_usd']:.2f} ({row['cost_in_eth']:.6f} ETH)")
    
    print("\n💡 TRANSACTION RECOMMENDATION:")
    if diff > 5:  # Significant increase expected
        print("  🔴 Gas fees are expected to increase significantly.")
        print("  🔴 Consider executing urgent transactions now.")
        print("  🔴 For non-urgent transactions, consider waiting for lower fees.")
    elif diff < -5:  # Significant decrease expected
        print("  🟢 Gas fees are expected to decrease significantly.")
        print("  🟢 Consider delaying non-urgent transactions.")
        print("  🟢 Optimal transaction window may be approaching.")
    else:  # Relatively stable
        print("  ⚪ Gas fees are relatively stable.")
        print("  ⚪ Current conditions are suitable for most transactions.")
        print("  ⚪ Consider transaction priority and urgency.")
    
    print("=" * 60)

def main():
    """Main function to calculate and visualize transaction costs."""
    try:
        # Connect to Ethereum
        web3 = connect_to_ethereum()
        
        # Get current gas fee
        current_fee = get_current_gas_fee(web3)
        
        # Get ETH price
        eth_price = get_eth_price()
        
        # Try to get predicted fee from model
        try:
            model, scaler = load_model()
            # For demonstration, we'll use a simple prediction
            # In a real implementation, this would use the model
            predicted_fee = current_fee * 0.95  # Predict 5% decrease
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            # Fallback: use current fee with small variation
            predicted_fee = current_fee * 0.95
        
        # Calculate transaction costs
        costs_df = calculate_transaction_costs(current_fee, eth_price)
        
        # Visualize transaction costs
        costs_path = visualize_transaction_costs(costs_df, current_fee, eth_price)
        
        # Create cost comparison chart
        comparison_path = create_cost_comparison_chart(current_fee, predicted_fee, eth_price)
        
        # Display results
        display_results(current_fee, predicted_fee, eth_price, costs_path, comparison_path)
        
        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
