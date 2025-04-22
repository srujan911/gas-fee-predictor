#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Model Tests

This script contains unit tests for the gas fee prediction model.
It tests data loading, preprocessing, model training, and prediction.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error
import joblib

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from scripts.clean_data import clean_gas_data
from scripts.train_model import (
    load_and_preprocess_data,
    scale_features,
    train_model,
    evaluate_model
)

class TestGasFeeModel(unittest.TestCase):
    """Test cases for the gas fee prediction model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data and model."""
        # Create test data directory if it doesn't exist
        os.makedirs("tests/data", exist_ok=True)
        
        # Create a small test dataset
        cls.test_data = pd.DataFrame({
            "block_number": range(1000, 1100),
            "timestamp": pd.date_range(start="2025-01-01", periods=100, freq="5min"),
            "base_fee_gwei": np.random.uniform(20, 100, 100),
            "gas_used": np.random.randint(10000000, 30000000, 100),
            "gas_limit": np.random.randint(30000000, 40000000, 100),
            "tx_count": np.random.randint(100, 300, 100)
        })
        
        # Save test data
        cls.test_data.to_csv("tests/data/test_gas_fees.csv", index=False)
        cls.test_data_cleaned = cls.test_data.copy()
        cls.test_data_cleaned.to_csv("tests/data/test_gas_fees_cleaned.csv", index=False)

    def test_data_cleaning(self):
        """Test the data cleaning function."""
        # Add some missing values and duplicates to test data
        dirty_data = self.test_data.copy()
        dirty_data.loc[0:5, "base_fee_gwei"] = np.nan
        dirty_data = pd.concat([dirty_data, dirty_data.iloc[10:15]])
        dirty_data.to_csv("tests/data/dirty_data.csv", index=False)
        
        # Clean the data
        cleaned_data = clean_gas_data(
            input_path="tests/data/dirty_data.csv",
            output_path="tests/data/cleaned_output.csv"
        )
        
        # Check that missing values and duplicates were removed
        self.assertIsNotNone(cleaned_data)
        self.assertTrue(os.path.exists("tests/data/cleaned_output.csv"))
        self.assertEqual(cleaned_data.shape[0], self.test_data.shape[0] - 6)  # 6 rows with NaN
        self.assertFalse(cleaned_data.isnull().any().any())

    def test_data_preprocessing(self):
        """Test data preprocessing function."""
        X, y, df = load_and_preprocess_data("tests/data/test_gas_fees_cleaned.csv")
        
        # Check shapes
        self.assertEqual(X.shape[0], 100)
        self.assertEqual(y.shape[0], 100)
        self.assertEqual(X.shape[1], 5)  # 5 features
        
        # Check feature names
        self.assertListEqual(
            list(X.columns),
            ["timestamp", "block_number", "gas_used", "gas_limit", "tx_count"]
        )

    def test_feature_scaling(self):
        """Test feature scaling function."""
        X, y, _ = load_and_preprocess_data("tests/data/test_gas_fees_cleaned.csv")
        X_scaled, scaler = scale_features(X)
        
        # Check that scaled data has mean close to 0 and std close to 1
        self.assertAlmostEqual(X_scaled.mean(), 0, delta=0.1)
        self.assertAlmostEqual(X_scaled.std(), 1, delta=0.1)
        
        # Check that original data can be recovered
        X_recovered = scaler.inverse_transform(X_scaled)
        np.testing.assert_array_almost_equal(X.values, X_recovered)

    def test_model_training(self):
        """Test model training function."""
        X, y, _ = load_and_preprocess_data("tests/data/test_gas_fees_cleaned.csv")
        X_scaled, _ = scale_features(X)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = train_model(X_train, y_train, perform_grid_search=False)
        
        # Check that model was trained
        self.assertIsNotNone(model)
        
        # Check that model can make predictions
        y_pred = model.predict(X_test)
        self.assertEqual(len(y_pred), len(y_test))
        
        # Check that predictions are reasonable
        mae = mean_absolute_error(y_test, y_pred)
        self.assertLess(mae, 50)  # MAE should be less than 50 GWEI for random data

    def test_model_evaluation(self):
        """Test model evaluation function."""
        X, y, _ = load_and_preprocess_data("tests/data/test_gas_fees_cleaned.csv")
        X_scaled, _ = scale_features(X)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = train_model(X_train, y_train)
        
        # Evaluate model
        metrics = evaluate_model(model, X_test, y_test)
        
        # Check that metrics were calculated
        self.assertIn('mae', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('r2', metrics)
        self.assertIn('predictions', metrics)
        
        # Check that metrics are reasonable
        self.assertGreaterEqual(metrics['r2'], -1)  # R² should be at least -1
        self.assertLessEqual(metrics['r2'], 1)  # R² should be at most 1
        self.assertGreaterEqual(metrics['mae'], 0)  # MAE should be non-negative

    def test_model_serialization(self):
        """Test model serialization and loading."""
        X, y, _ = load_and_preprocess_data("tests/data/test_gas_fees_cleaned.csv")
        X_scaled, scaler = scale_features(X)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = train_model(X_train, y_train)
        
        # Save model
        os.makedirs("tests/models", exist_ok=True)
        joblib.dump((model, scaler), "tests/models/test_model.pkl")
        
        # Load model
        loaded_model, loaded_scaler = joblib.load("tests/models/test_model.pkl")
        
        # Check that loaded model makes the same predictions
        y_pred_original = model.predict(X_test)
        y_pred_loaded = loaded_model.predict(X_test)
        np.testing.assert_array_almost_equal(y_pred_original, y_pred_loaded)
        
        # Check that loaded scaler transforms data the same way
        X_scaled_original = scaler.transform(X.iloc[:5])
        X_scaled_loaded = loaded_scaler.transform(X.iloc[:5])
        np.testing.assert_array_almost_equal(X_scaled_original, X_scaled_loaded)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files."""
        # Remove test data files
        test_files = [
            "tests/data/test_gas_fees.csv",
            "tests/data/test_gas_fees_cleaned.csv",
            "tests/data/dirty_data.csv",
            "tests/data/cleaned_output.csv",
            "tests/models/test_model.pkl"
        ]
        
        for file in test_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        # Remove test directories
        for directory in ["tests/data", "tests/models"]:
            try:
                os.rmdir(directory)
            except:
                pass

if __name__ == "__main__":
    unittest.main()
