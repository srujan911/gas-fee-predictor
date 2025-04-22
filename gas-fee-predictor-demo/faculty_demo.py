#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Faculty Demonstration Script

This script provides an easy way to run the gas fee prediction pipeline
with a configurable number of blocks for faculty demonstrations.

Author: SRUJANJAINI
Date: April 2025
"""

import argparse
import os
import subprocess
import time
import webbrowser
from datetime import datetime

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run gas fee prediction for faculty demonstration")
    parser.add_argument("-n", "--num-blocks", type=int, default=50,
                        help="Number of blocks to collect (default: 50)")
    parser.add_argument("-t", "--timezone", type=str, default="Asia/Kolkata",
                        help="Timezone for visualization (default: Asia/Kolkata)")
    parser.add_argument("-f", "--full", action="store_true",
                        help="Run full pipeline (collect, clean, train, predict, visualize)")
    parser.add_argument("-c", "--collect-only", action="store_true",
                        help="Only collect data, don't train model")
    parser.add_argument("-p", "--predict-only", action="store_true",
                        help="Only make a prediction using existing model")
    parser.add_argument("-i", "--improved", action="store_true",
                        help="Use improved gas fee prediction")
    parser.add_argument("-v", "--visualize-only", action="store_true",
                        help="Only generate visualizations")
    parser.add_argument("--heatmap", action="store_true",
                        help="Generate gas fee heatmap analysis")
    parser.add_argument("--dashboard", action="store_true",
                        help="Generate interactive dashboard")
    parser.add_argument("--costs", action="store_true",
                        help="Generate transaction cost calculator")
    parser.add_argument("--models", action="store_true",
                        help="Generate model comparison visualization")
    parser.add_argument("--all-viz", action="store_true",
                        help="Generate all visualizations")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't open visualizations in browser")
    return parser.parse_args()

def run_command(command):
    """Run a command and print its output."""
    print(f"\n> Running: {command}")
    start_time = time.time()
    result = subprocess.run(command, shell=True, text=True)
    elapsed = time.time() - start_time
    print(f"> Command completed in {elapsed:.2f} seconds with exit code {result.returncode}")
    return result.returncode

def create_visualization_html():
    """Create an HTML file to display all visualizations for faculty demo."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ethereum Gas Fee Predictor - Faculty Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .section {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
                width: 100%;
            }
            .section h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .viz-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .viz-item {
                margin: 10px;
                text-align: center;
            }
            .viz-item img {
                max-width: 100%;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .viz-item h3 {
                margin-top: 10px;
                color: #2c3e50;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Ethereum Gas Fee Predictor - Faculty Demo</h1>
            <p>A comprehensive visualization dashboard for the Ethereum Gas Fee Predictor project</p>
        </div>

        <div class="container">
            <!-- Basic Visualizations Section -->
            <div class="section">
                <h2>Basic Visualizations</h2>
                <div class="viz-container">
                    <div class="viz-item">
                        <img src="gas_fees.png" alt="Gas Fee Time Series">
                        <h3>Gas Fee Time Series</h3>
                        <p>Historical gas fee trends over time</p>
                    </div>
                    <div class="viz-item">
                        <img src="comparison.png" alt="Prediction Comparison">
                        <h3>Prediction Comparison</h3>
                        <p>Comparison of predicted vs actual gas fees</p>
                    </div>
                </div>
            </div>

            <!-- Heatmap Analysis Section -->
            <div class="section">
                <h2>Gas Fee Heatmap Analysis</h2>
                <div class="viz-container">
                    <div class="viz-item">
                        <img src="gas_fee_heatmap.png" alt="Gas Fee Heatmap">
                        <h3>Gas Fee Heatmap by Day and Hour</h3>
                        <p>Identifies optimal times to transact based on historical patterns</p>
                    </div>
                </div>
            </div>

            <!-- Dashboard Section -->
            <div class="section">
                <h2>Interactive Dashboard</h2>
                <div class="viz-container">
                    <div class="viz-item">
                        <img src="dashboard.png" alt="Interactive Dashboard">
                        <h3>Comprehensive Dashboard</h3>
                        <p>Multiple visualizations of gas fee data and predictions</p>
                    </div>
                    <div class="viz-item">
                        <img src="dashboard/time_series.png" alt="Time Series">
                        <h3>Time Series Analysis</h3>
                        <p>Detailed view of recent gas fee trends</p>
                    </div>
                    <div class="viz-item">
                        <img src="dashboard/distribution.png" alt="Distribution">
                        <h3>Gas Fee Distribution</h3>
                        <p>Statistical distribution of gas fees</p>
                    </div>
                </div>
            </div>

            <!-- Transaction Cost Section -->
            <div class="section">
                <h2>Transaction Cost Calculator</h2>
                <div class="viz-container">
                    <div class="viz-item">
                        <img src="transaction_costs.png" alt="Transaction Costs">
                        <h3>Transaction Costs by Type</h3>
                        <p>Cost estimates for different transaction types</p>
                    </div>
                    <div class="viz-item">
                        <img src="cost_comparison.png" alt="Cost Comparison">
                        <h3>Cost Comparison</h3>
                        <p>Comparison of costs with current vs predicted fees</p>
                    </div>
                </div>
            </div>

            <!-- Model Comparison Section -->
            <div class="section">
                <h2>Model Comparison</h2>
                <div class="viz-container">
                    <div class="viz-item">
                        <img src="model_comparison.png" alt="Model Comparison">
                        <h3>Prediction Approach Comparison</h3>
                        <p>Comparison of different prediction approaches</p>
                    </div>
                    <div class="viz-item">
                        <img src="model_metrics.png" alt="Model Metrics">
                        <h3>Performance Metrics</h3>
                        <p>Evaluation metrics for different prediction approaches</p>
                    </div>
                    <div class="viz-item">
                        <img src="error_distribution.png" alt="Error Distribution">
                        <h3>Error Distribution</h3>
                        <p>Distribution of prediction errors across models</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Ethereum Gas Fee Predictor - Created by SRUJANJAINI</p>
            <p>Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </body>
    </html>
    """
    return html_content

def open_visualization_dashboard():
    """Open the visualization dashboard in the default browser."""
    try:
        # Create a simple HTML file to display all visualizations
        html_content = create_visualization_html()
        html_path = os.path.join(os.getcwd(), "visualizations", "faculty_demo.html")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(html_path), exist_ok=True)

        # Write HTML file with UTF-8 encoding
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Open the HTML file in the default browser
        print(f"Opening visualization dashboard at: {html_path}")
        webbrowser.open(f"file://{html_path}")
        return True
    except Exception as e:
        print(f"Error opening visualizations: {e}")
        return False

def main():
    """Main function to run the demonstration."""
    args = parse_arguments()

    # Print banner
    print("\n" + "=" * 60)
    print("🎓 ETHEREUM GAS FEE PREDICTOR - FACULTY DEMONSTRATION 🎓")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Number of blocks: {args.num_blocks}")
    print(f"Timezone: {args.timezone}")
    print("-" * 60)

    # Print explanation about feature importance
    if args.full or not (args.collect_only or args.predict_only or args.visualize_only):
        print("\nNOTE ABOUT FEATURE IMPORTANCE:")
        print("When you see feature importance values (e.g., gas_used: 0.2871), these")
        print("represent the relative importance of each feature in the prediction model,")
        print("NOT the actual values of these features. Values range from 0 to 1, with")
        print("higher values indicating greater importance in making predictions.")
        print("The sum of all importance values equals 1 (or 100%).")
        print("-" * 60)

    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("visualizations", exist_ok=True)

    # Run the appropriate commands based on arguments
    if args.full:
        # Run full pipeline
        print("\n📡 STEP 1: COLLECTING GAS FEE DATA")
        run_command(f"python scripts/collect_gas_data.py -n {args.num_blocks} -t {args.timezone}")

        print("\n🧹 STEP 2: CLEANING DATA")
        run_command("python scripts/clean_data.py")

        print("\n🧠 STEP 3: TRAINING MODEL")
        run_command("python scripts/train_model.py")

        print("\n🔮 STEP 4: MAKING PREDICTION")
        if args.improved:
            print("Using improved prediction model")
            run_command("python scripts/improved_gas_fee.py")
        else:
            run_command("python scripts/get_gas_fee_new.py")

        print("\n📊 STEP 5: GENERATING VISUALIZATIONS")
        run_command("python scripts/add_predictions_to_csv.py")
        run_command(f"python scripts/visualize_gas_fees.py -t {args.timezone} -s visualizations/gas_fees.png")
        run_command(f"python scripts/visualize_comparison.py -t {args.timezone} -s visualizations/comparison.png")

        print("\n📊 STEP 6: GENERATING ADVANCED VISUALIZATIONS")
        print("\n📊 6.1: GENERATING GAS FEE HEATMAP ANALYSIS")
        run_command("python scripts/generate_gas_heatmap.py")
        print("\n📊 6.2: GENERATING INTERACTIVE DASHBOARD")
        run_command("python scripts/interactive_dashboard.py")
        print("\n📊 6.3: GENERATING TRANSACTION COST CALCULATOR")
        run_command("python scripts/transaction_cost_calculator.py")
        print("\n📊 6.4: GENERATING MODEL COMPARISON VISUALIZATION")
        run_command("python scripts/model_comparison.py")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    elif args.collect_only:
        # Only collect data
        print("\n📡 COLLECTING GAS FEE DATA")
        run_command(f"python scripts/collect_gas_data.py -n {args.num_blocks} -t {args.timezone}")

    elif args.predict_only:
        # Only make prediction
        print("\n🔮 MAKING PREDICTION")
        if args.improved:
            print("Using improved prediction model")
            run_command("python scripts/improved_gas_fee.py")
        else:
            run_command("python scripts/get_gas_fee_new.py")

    elif args.visualize_only:
        # Only generate visualizations
        print("\n📊 GENERATING VISUALIZATIONS")
        run_command("python scripts/add_predictions_to_csv.py")
        run_command(f"python scripts/visualize_gas_fees.py -t {args.timezone} -s visualizations/gas_fees.png")
        run_command(f"python scripts/visualize_comparison.py -t {args.timezone} -s visualizations/comparison.png")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    elif args.heatmap:
        # Generate gas fee heatmap
        print("\n📊 GENERATING GAS FEE HEATMAP ANALYSIS")
        run_command("python scripts/generate_gas_heatmap.py")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    elif args.dashboard:
        # Generate interactive dashboard
        print("\n📊 GENERATING INTERACTIVE DASHBOARD")
        run_command("python scripts/interactive_dashboard.py")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    elif args.costs:
        # Generate transaction cost calculator
        print("\n📊 GENERATING TRANSACTION COST CALCULATOR")
        run_command("python scripts/transaction_cost_calculator.py")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    elif args.models:
        # Generate model comparison visualization
        print("\n📊 GENERATING MODEL COMPARISON VISUALIZATION")
        run_command("python scripts/model_comparison.py")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    elif args.all_viz:
        # Generate all visualizations
        print("\n📊 GENERATING ALL VISUALIZATIONS")
        print("\n📊 1. GENERATING GAS FEE HEATMAP ANALYSIS")
        run_command("python scripts/generate_gas_heatmap.py")
        print("\n📊 2. GENERATING INTERACTIVE DASHBOARD")
        run_command("python scripts/interactive_dashboard.py")
        print("\n📊 3. GENERATING TRANSACTION COST CALCULATOR")
        run_command("python scripts/transaction_cost_calculator.py")
        print("\n📊 4. GENERATING MODEL COMPARISON VISUALIZATION")
        run_command("python scripts/model_comparison.py")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    else:
        # Default: collect data and make prediction
        print("\n📡 STEP 1: COLLECTING GAS FEE DATA")
        run_command(f"python scripts/collect_gas_data.py -n {args.num_blocks} -t {args.timezone}")

        print("\n🧹 STEP 2: CLEANING DATA")
        run_command("python scripts/clean_data.py")

        print("\n🔮 STEP 3: MAKING PREDICTION")
        if args.improved:
            print("Using improved prediction model")
            run_command("python scripts/improved_gas_fee.py")
        else:
            run_command("python scripts/get_gas_fee_new.py")

        # Generate basic visualizations
        print("\n📊 STEP 4: GENERATING BASIC VISUALIZATIONS")
        run_command("python scripts/add_predictions_to_csv.py")
        run_command(f"python scripts/visualize_gas_fees.py -t {args.timezone} -s visualizations/gas_fees.png")
        run_command(f"python scripts/visualize_comparison.py -t {args.timezone} -s visualizations/comparison.png")

        # Open visualizations for faculty demo
        if not args.no_browser:
            print("\n💻 OPENING VISUALIZATIONS FOR FACULTY DEMO")
            open_visualization_dashboard()

    # Print summary
    print("\n" + "=" * 60)
    print("🎓 DEMONSTRATION COMPLETED 🎓")
    print("=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    exit(main())
