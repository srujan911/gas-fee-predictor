"""
Test App for Ethereum Gas Fee Predictor

This script tests the functionality of the Ethereum Gas Fee Predictor app.
It verifies that all routes and features are working correctly.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import sys
import unittest
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask
import tempfile
import shutil

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app (assuming app.py is in the parent directory)
from app import app as flask_app

class TestGasFeePredictor(unittest.TestCase):
    """Test cases for the Ethereum Gas Fee Predictor app."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test client
        self.app = flask_app.test_client()
        self.app.testing = True
        
        # Create temporary directories for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.models_dir = os.path.join(self.temp_dir, 'models')
        self.visualizations_dir = os.path.join(self.temp_dir, 'visualizations')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.visualizations_dir, exist_ok=True)
        
        # Create sample data
        self.create_sample_data()
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
        
    def create_sample_data(self):
        """Create sample data for testing."""
        # Create sample historical gas data
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
        df.to_csv(os.path.join(self.data_dir, 'historical_gas_data.csv'), index=False)
        
        # Create sample prediction data
        df['predicted_fee'] = df['base_fee_gwei'] * np.random.normal(1, 0.05, size=len(df))
        df['prediction_error'] = df['base_fee_gwei'] - df['predicted_fee']
        df['prediction_error_pct'] = (df['prediction_error'] / df['base_fee_gwei']) * 100
        
        # Save sample prediction data
        df.to_csv(os.path.join(self.data_dir, 'gas_fee_predictions.csv'), index=False)
        
    def test_index_route(self):
        """Test the index route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_dashboard_route(self):
        """Test the dashboard route."""
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
    def test_app_route(self):
        """Test the app route."""
        response = self.app.get('/app')
        self.assertEqual(response.status_code, 200)
        
    def test_predict_route(self):
        """Test the predict route."""
        response = self.app.get('/predict')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('prediction' in data)
        
        # Check prediction fields
        prediction = data['prediction']
        self.assertTrue('current_fee' in prediction)
        self.assertTrue('predicted_fee' in prediction)
        self.assertTrue('block_number' in prediction)
        self.assertTrue('gas_used' in prediction)
        self.assertTrue('gas_limit' in prediction)
        self.assertTrue('tx_count' in prediction)
        
    def test_heatmap_route(self):
        """Test the heatmap route."""
        response = self.app.get('/heatmap')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('heatmap_path' in data)
        self.assertTrue('best_time' in data)
        self.assertTrue('worst_time' in data)
        self.assertTrue('optimal_times' in data)
        self.assertTrue('avoid_times' in data)
        
    def test_transaction_costs_route(self):
        """Test the transaction costs route."""
        response = self.app.get('/transaction-costs')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('current_costs' in data)
        self.assertTrue('optimal_costs' in data)
        
    def test_block_stats_route(self):
        """Test the block stats route."""
        response = self.app.get('/block-stats')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('latest_block' in data)
        self.assertTrue('blocks' in data)
        
    def test_gas_fee_history_route(self):
        """Test the gas fee history route."""
        response = self.app.get('/gas-fee-history')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('history' in data)
        self.assertTrue('statistics' in data)
        
    def test_run_heatmap_script_route(self):
        """Test the run heatmap script route."""
        response = self.app.post('/run-heatmap-script')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue('heatmap_path' in data)
        
    def test_optimal_times_route(self):
        """Test the optimal times route."""
        response = self.app.get('/optimal-times')
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        data = json.loads(response.data)
        
        # Check response structure
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('optimal_times' in data)
        self.assertTrue('avoid_times' in data)
        
if __name__ == '__main__':
    unittest.main()
