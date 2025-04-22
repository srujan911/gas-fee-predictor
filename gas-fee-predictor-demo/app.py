#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Web Frontend

This script creates a web-based frontend for the Ethereum Gas Fee Predictor project
using Flask.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

# Import project modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from improved_gas_fee import predict_gas_fee, connect_to_ethereum, load_model
from generate_gas_heatmap import load_historical_data, generate_gas_fee_heatmap, find_optimal_transaction_times
from transaction_cost_calculator import calculate_transaction_costs, get_eth_price

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ethereum-gas-fee-predictor'
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs(os.path.join('static', 'images'), exist_ok=True)
os.makedirs(os.path.join('static', 'js'), exist_ok=True)
os.makedirs(os.path.join('static', 'css'), exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Global variables
last_prediction = None
last_prediction_time = None

@app.route('/')
def index():
    """Render the main landing page."""
    return render_template('index.html')

@app.route('/app')
def app_page():
    """Render the main application page with all features."""
    return render_template('app.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Handle gas fee prediction requests."""
    global last_prediction, last_prediction_time

    if request.method == 'POST':
        try:
            # Load model
            model, scaler = load_model()

            # Connect to Ethereum
            web3 = connect_to_ethereum()

            # Make prediction
            predicted_fee, block_data = predict_gas_fee(web3, model, scaler)

            # Get current time
            current_time = datetime.now()

            # Store prediction
            last_prediction = {
                'predicted_fee': float(predicted_fee),
                'current_fee': float(block_data['base_fee_gwei']),
                'block_number': int(block_data['block_number']),
                'gas_used': int(block_data['gas_used']),
                'gas_limit': int(block_data['gas_limit']),
                'tx_count': int(block_data['tx_count']),
                'timestamp': int(block_data['timestamp']),
                'formatted_time': datetime.fromtimestamp(block_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            }
            last_prediction_time = current_time

            # Calculate difference
            difference = predicted_fee - block_data['base_fee_gwei']
            percent_change = (difference / block_data['base_fee_gwei']) * 100 if block_data['base_fee_gwei'] > 0 else 0

            last_prediction['difference'] = float(difference)
            last_prediction['percent_change'] = float(percent_change)

            return jsonify({
                'success': True,
                'prediction': last_prediction
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    else:
        # GET request - return the last prediction if available
        if last_prediction and last_prediction_time:
            # Check if prediction is still fresh (less than 5 minutes old)
            if datetime.now() - last_prediction_time < timedelta(minutes=5):
                return jsonify({
                    'success': True,
                    'prediction': last_prediction,
                    'cached': True
                })

        # No fresh prediction available
        return jsonify({
            'success': False,
            'error': 'No recent prediction available'
        })

@app.route('/heatmap')
def heatmap():
    """Generate and return gas fee heatmap data."""
    try:
        # Load historical data
        df = load_historical_data()

        # Convert UTC timestamps to IST for heatmap
        if 'timestamp' in df.columns:
            # Ensure timestamp is datetime with timezone info
            if not pd.api.types.is_datetime64_ns_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            elif not df['timestamp'].dt.tz:
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')

            # Convert to IST
            df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')

        # Generate heatmap with IST timezone
        output_dir = os.path.join(os.getcwd(), 'static', 'images')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'gas_fee_heatmap.png')

        # Log the output path for debugging
        print(f"Generating heatmap at: {output_path}")

        # Generate the heatmap
        heatmap_results = generate_gas_fee_heatmap(df, output_path=output_path)

        # Verify the file was created
        if os.path.exists(output_path):
            print(f"Heatmap file created successfully at: {output_path}")
        else:
            print(f"WARNING: Heatmap file was not created at: {output_path}")

        # Find optimal transaction times
        optimal_times = find_optimal_transaction_times(df)

        return jsonify({
            'success': True,
            'heatmap_path': '/static/images/gas_fee_heatmap.png',
            'best_time': heatmap_results['best_time'],
            'worst_time': heatmap_results['worst_time'],
            'optimal_times': optimal_times['optimal_times'][:5],
            'avoid_times': optimal_times['avoid_times'][:5],
            'timezone': 'Asia/Kolkata'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/transaction-costs')
def transaction_costs():
    """Calculate and return transaction costs."""
    try:
        # Get current gas fee from last prediction or use a default
        if last_prediction:
            current_fee = last_prediction['current_fee']
            predicted_fee = last_prediction['predicted_fee']
        else:
            # Use default values if no prediction is available
            current_fee = 50.0
            predicted_fee = 45.0

        # Get ETH price
        eth_price = get_eth_price()

        # Calculate costs for current fee
        current_costs = calculate_transaction_costs(current_fee, eth_price)

        # Calculate costs for predicted fee
        predicted_costs = calculate_transaction_costs(predicted_fee, eth_price)

        # Convert to list of dictionaries for JSON serialization
        current_costs_list = current_costs.to_dict('records')
        predicted_costs_list = predicted_costs.to_dict('records')

        return jsonify({
            'success': True,
            'eth_price': eth_price,
            'current_fee': current_fee,
            'predicted_fee': predicted_fee,
            'current_costs': current_costs_list,
            'predicted_costs': predicted_costs_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/historical-data')
def historical_data():
    """Return historical gas fee data for charts."""
    try:
        # Load historical data
        df = pd.read_csv('data/gas_fees_cleaned.csv')

        # Convert timestamp to datetime with UTC timezone
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # Convert to IST timezone
        df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')

        # Sort by timestamp
        df = df.sort_values('timestamp')

        # Get the most recent 100 records for the chart
        recent_df = df.tail(100)

        # Prepare data for JSON
        chart_data = {
            'timestamps': recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'base_fees': recent_df['base_fee_gwei'].tolist()
        }

        # Add predictions if available
        if 'predicted_fee' in recent_df.columns:
            chart_data['predicted_fees'] = recent_df['predicted_fee'].tolist()

        # Calculate hourly averages using IST hours
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['base_fee_gwei'].mean().reset_index()

        hourly_data = {
            'hours': hourly_avg['hour'].tolist(),
            'avg_fees': hourly_avg['base_fee_gwei'].tolist(),
            'timezone': 'Asia/Kolkata'
        }

        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'hourly_data': hourly_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/upload-data', methods=['POST'])
def upload_data():
    """Handle data file uploads."""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file part'
        })

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No selected file'
        })

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return jsonify({
            'success': True,
            'message': f'File {filename} uploaded successfully',
            'file_path': file_path
        })

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """Run the full prediction pipeline."""
    try:
        # Get parameters from request
        data = request.get_json()
        num_blocks = data.get('num_blocks', 200)  # Increased default from 50 to 200
        use_improved = data.get('use_improved', True)
        timezone = data.get('timezone', 'Asia/Kolkata')  # Default to IST timezone

        # Import run_pipeline module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from run_pipeline import run_data_collection, run_data_cleaning, run_model_training, run_prediction

        # Run pipeline steps
        collection_success = run_data_collection(num_blocks=num_blocks, timezone=timezone)
        if not collection_success:
            return jsonify({
                'success': False,
                'error': 'Data collection failed'
            })

        cleaning_success = run_data_cleaning()
        if not cleaning_success:
            return jsonify({
                'success': False,
                'error': 'Data cleaning failed'
            })

        training_success = run_model_training()
        if not training_success:
            return jsonify({
                'success': False,
                'error': 'Model training failed'
            })

        prediction_success = run_prediction(use_improved=use_improved)
        if not prediction_success:
            return jsonify({
                'success': False,
                'error': 'Prediction failed'
            })

        return jsonify({
            'success': True,
            'message': 'Pipeline completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/run-heatmap-script', methods=['POST'])
def run_heatmap_script():
    """Run the heatmap generation script directly."""
    try:
        # Import the script
        from scripts.generate_gas_heatmap import main as generate_heatmap_main

        # Run the script
        result = generate_heatmap_main()

        if result == 0:
            return jsonify({
                'success': True,
                'message': 'Heatmap generated successfully',
                'heatmap_path': '/static/images/gas_fee_heatmap.png'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Heatmap generation failed with code ' + str(result)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
