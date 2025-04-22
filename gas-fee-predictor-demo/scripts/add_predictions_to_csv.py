#!/usr/bin/env python3
"""
Ethereum Gas Fee Predictor - Add Predictions to CSV

This script loads the trained model and adds predictions to the cleaned gas fee data.
It handles timestamp conversion correctly and saves the results to a new CSV file.

Author: SRUJANJAINI
Date: April 2025
"""

import pandas as pd
import joblib
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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

def load_data(data_path="data/gas_fees_cleaned.csv"):
    """Load the cleaned gas fee data."""
    try:
        if not os.path.exists(data_path):
            logger.error(f"Data file not found: {data_path}")
            raise FileNotFoundError(f"Data file not found: {data_path}")

        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def prepare_features(df, feature_names=["timestamp", "block_number", "gas_used", "gas_limit", "tx_count"]):
    """Prepare features for prediction."""
    try:
        logger.info("Preparing features for prediction")

        # Check if all required features are present
        missing_features = [f for f in feature_names if f not in df.columns]
        if missing_features:
            logger.error(f"Missing features in data: {missing_features}")
            raise ValueError(f"Missing features in data: {missing_features}")

        # Drop rows with missing values in feature columns
        df = df.dropna(subset=feature_names)
        logger.info(f"Data shape after dropping rows with missing features: {df.shape}")

        # Extract features
        X = df[feature_names].copy()

        # Ensure block_number is an integer
        if "block_number" in feature_names:
            logger.info("Ensuring block_number is an integer")
            X["block_number"] = X["block_number"].astype(int)

        # Convert timestamp to datetime and then to unix timestamp
        if "timestamp" in feature_names:
            logger.info("Converting timestamp to unix format")
            X["timestamp"] = pd.to_datetime(X["timestamp"], errors="coerce", utc=True)
            X = X.dropna(subset=["timestamp"])

            # Convert to unix timestamp (seconds since epoch)
            X["timestamp"] = X["timestamp"].map(lambda x: int(x.timestamp()))

        # Ensure other numeric columns are integers
        for col in ["gas_used", "gas_limit", "tx_count"]:
            if col in feature_names:
                logger.info(f"Ensuring {col} is an integer")
                X[col] = X[col].astype(int)

        logger.info(f"Prepared features with shape: {X.shape}")
        return X, df
    except Exception as e:
        logger.error(f"Error preparing features: {e}")
        raise

def add_predictions(df, X, model, scaler):
    """Add predictions to the dataframe."""
    try:
        logger.info("Scaling features and making predictions")

        # Scale features
        X_scaled = scaler.transform(X)

        # Make predictions
        predictions = model.predict(X_scaled)

        # Add predictions to dataframe
        df["predicted_fee"] = predictions

        # Ensure predictions are non-negative
        df["predicted_fee"] = df["predicted_fee"].clip(lower=0)

        # Calculate error metrics
        if "base_fee_gwei" in df.columns:
            mae = (df["base_fee_gwei"] - df["predicted_fee"]).abs().mean()
            rmse = ((df["base_fee_gwei"] - df["predicted_fee"]) ** 2).mean() ** 0.5
            logger.info(f"Prediction metrics - MAE: {mae:.2f} GWEI, RMSE: {rmse:.2f} GWEI")

        logger.info(f"Added predictions to dataframe")
        return df
    except Exception as e:
        logger.error(f"Error adding predictions: {e}")
        raise

def save_results(df, output_path="data/gas_fees_with_predictions.csv"):
    """Save the dataframe with predictions to CSV."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Saving results to {output_path}")
        df.to_csv(output_path, index=False)
        logger.info(f"Results saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

def main():
    """Main function to add predictions to CSV."""
    try:
        # Load model and scaler
        model, scaler = load_model()

        # Load data
        df = load_data()

        # Prepare features
        X, df = prepare_features(df)

        # Add predictions
        df = add_predictions(df, X, model, scaler)

        # Save results
        output_path = "data/gas_fees_with_predictions.csv"
        save_results(df, output_path)

        # Print success message
        print("\n" + "=" * 50)
        print("🔮 ETHEREUM GAS FEE PREDICTIONS 🔮")
        print("=" * 50)
        print(f"✅ Successfully added predictions to {df.shape[0]} records")
        print(f"💾 Results saved to: {output_path}")
        print("=" * 50)

        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
