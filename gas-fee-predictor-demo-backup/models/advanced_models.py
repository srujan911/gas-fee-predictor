"""
Advanced prediction models for Ethereum gas fee prediction.
This module implements more sophisticated machine learning models
including LSTM networks and ensemble methods.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMModel:
    """LSTM neural network for time series prediction of gas fees."""
    
    def __init__(self, sequence_length=24):
        """
        Initialize the LSTM model.
        
        Args:
            sequence_length (int): Number of time steps to look back for prediction
        """
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def _create_sequences(self, data):
        """
        Create sequences for LSTM input.
        
        Args:
            data (array): Input time series data
            
        Returns:
            tuple: X (sequences) and y (target values)
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """
        Build the LSTM model architecture.
        
        Args:
            input_shape (tuple): Shape of input data (sequence_length, features)
            
        Returns:
            model: Compiled Keras model
        """
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train(self, data, epochs=50, batch_size=32, validation_split=0.2):
        """
        Train the LSTM model.
        
        Args:
            data (DataFrame): DataFrame with 'timestamp' and 'base_fee_gwei' columns
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            history: Training history
        """
        try:
            # Extract and scale the data
            values = data['base_fee_gwei'].values.reshape(-1, 1)
            scaled_data = self.scaler.fit_transform(values)
            
            # Create sequences
            X, y = self._create_sequences(scaled_data)
            
            # Reshape for LSTM [samples, time steps, features]
            X = X.reshape(X.shape[0], X.shape[1], 1)
            
            # Split into train and validation sets
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, shuffle=False
            )
            
            # Build model
            self.model = self.build_model((self.sequence_length, 1))
            
            # Early stopping to prevent overfitting
            early_stop = EarlyStopping(
                monitor='val_loss', patience=10, restore_best_weights=True
            )
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val, y_val),
                callbacks=[early_stop],
                verbose=1
            )
            
            logger.info("LSTM model training completed successfully")
            return history
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            raise
    
    def predict(self, data):
        """
        Make predictions with the trained LSTM model.
        
        Args:
            data (DataFrame): DataFrame with recent gas fee data
            
        Returns:
            float: Predicted gas fee
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        try:
            # Extract and scale the data
            values = data['base_fee_gwei'].values.reshape(-1, 1)
            scaled_data = self.scaler.transform(values)
            
            # Take the last sequence_length values
            sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)
            
            # Make prediction
            scaled_prediction = self.model.predict(sequence)
            
            # Inverse transform to get the actual prediction
            prediction = self.scaler.inverse_transform(scaled_prediction)[0, 0]
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction with LSTM model: {e}")
            raise
    
    def save(self, model_path, scaler_path):
        """
        Save the model and scaler.
        
        Args:
            model_path (str): Path to save the model
            scaler_path (str): Path to save the scaler
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save model and scaler
            self.model.save(model_path)
            joblib.dump(self.scaler, scaler_path)
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Scaler saved to {scaler_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load(self, model_path, scaler_path):
        """
        Load the model and scaler.
        
        Args:
            model_path (str): Path to the saved model
            scaler_path (str): Path to the saved scaler
        """
        try:
            # Load model and scaler
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Scaler loaded from {scaler_path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise


class GRUModel:
    """GRU neural network for time series prediction of gas fees."""
    
    def __init__(self, sequence_length=24):
        """
        Initialize the GRU model.
        
        Args:
            sequence_length (int): Number of time steps to look back for prediction
        """
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def _create_sequences(self, data):
        """
        Create sequences for GRU input.
        
        Args:
            data (array): Input time series data
            
        Returns:
            tuple: X (sequences) and y (target values)
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """
        Build the GRU model architecture.
        
        Args:
            input_shape (tuple): Shape of input data (sequence_length, features)
            
        Returns:
            model: Compiled Keras model
        """
        model = Sequential()
        model.add(GRU(50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(GRU(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train(self, data, epochs=50, batch_size=32, validation_split=0.2):
        """
        Train the GRU model.
        
        Args:
            data (DataFrame): DataFrame with 'timestamp' and 'base_fee_gwei' columns
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            history: Training history
        """
        try:
            # Extract and scale the data
            values = data['base_fee_gwei'].values.reshape(-1, 1)
            scaled_data = self.scaler.fit_transform(values)
            
            # Create sequences
            X, y = self._create_sequences(scaled_data)
            
            # Reshape for GRU [samples, time steps, features]
            X = X.reshape(X.shape[0], X.shape[1], 1)
            
            # Split into train and validation sets
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, shuffle=False
            )
            
            # Build model
            self.model = self.build_model((self.sequence_length, 1))
            
            # Early stopping to prevent overfitting
            early_stop = EarlyStopping(
                monitor='val_loss', patience=10, restore_best_weights=True
            )
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val, y_val),
                callbacks=[early_stop],
                verbose=1
            )
            
            logger.info("GRU model training completed successfully")
            return history
            
        except Exception as e:
            logger.error(f"Error training GRU model: {e}")
            raise
    
    def predict(self, data):
        """
        Make predictions with the trained GRU model.
        
        Args:
            data (DataFrame): DataFrame with recent gas fee data
            
        Returns:
            float: Predicted gas fee
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        try:
            # Extract and scale the data
            values = data['base_fee_gwei'].values.reshape(-1, 1)
            scaled_data = self.scaler.transform(values)
            
            # Take the last sequence_length values
            sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)
            
            # Make prediction
            scaled_prediction = self.model.predict(sequence)
            
            # Inverse transform to get the actual prediction
            prediction = self.scaler.inverse_transform(scaled_prediction)[0, 0]
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction with GRU model: {e}")
            raise
    
    def save(self, model_path, scaler_path):
        """
        Save the model and scaler.
        
        Args:
            model_path (str): Path to save the model
            scaler_path (str): Path to save the scaler
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save model and scaler
            self.model.save(model_path)
            joblib.dump(self.scaler, scaler_path)
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Scaler saved to {scaler_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load(self, model_path, scaler_path):
        """
        Load the model and scaler.
        
        Args:
            model_path (str): Path to the saved model
            scaler_path (str): Path to the saved scaler
        """
        try:
            # Load model and scaler
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Scaler loaded from {scaler_path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise


class EnsembleModel:
    """Ensemble model combining multiple prediction models."""
    
    def __init__(self):
        """Initialize the ensemble model."""
        self.models = []
        self.weights = []
        
    def add_model(self, model, weight=1.0):
        """
        Add a model to the ensemble.
        
        Args:
            model: Prediction model with a predict method
            weight (float): Weight for this model in the ensemble
        """
        self.models.append(model)
        self.weights.append(weight)
        
    def normalize_weights(self):
        """Normalize weights to sum to 1."""
        total = sum(self.weights)
        self.weights = [w / total for w in self.weights]
        
    def predict(self, data):
        """
        Make predictions with the ensemble model.
        
        Args:
            data (DataFrame): DataFrame with recent gas fee data
            
        Returns:
            float: Predicted gas fee
        """
        if not self.models:
            raise ValueError("No models in the ensemble")
        
        try:
            # Normalize weights
            self.normalize_weights()
            
            # Get predictions from all models
            predictions = []
            for model in self.models:
                pred = model.predict(data)
                predictions.append(pred)
            
            # Weighted average of predictions
            weighted_pred = sum(p * w for p, w in zip(predictions, self.weights))
            
            return weighted_pred
            
        except Exception as e:
            logger.error(f"Error making prediction with ensemble model: {e}")
            raise


def train_random_forest(data, n_estimators=100, max_depth=None):
    """
    Train a Random Forest model for gas fee prediction.
    
    Args:
        data (DataFrame): DataFrame with features and target
        n_estimators (int): Number of trees in the forest
        max_depth (int): Maximum depth of the trees
        
    Returns:
        model: Trained Random Forest model
    """
    try:
        # Prepare features
        X = prepare_features(data)
        y = data['base_fee_gwei'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate model
        score = model.score(X_test, y_test)
        logger.info(f"Random Forest R² score: {score:.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training Random Forest model: {e}")
        raise


def train_gradient_boosting(data, n_estimators=100, learning_rate=0.1, max_depth=3):
    """
    Train a Gradient Boosting model for gas fee prediction.
    
    Args:
        data (DataFrame): DataFrame with features and target
        n_estimators (int): Number of boosting stages
        learning_rate (float): Learning rate
        max_depth (int): Maximum depth of the trees
        
    Returns:
        model: Trained Gradient Boosting model
    """
    try:
        # Prepare features
        X = prepare_features(data)
        y = data['base_fee_gwei'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Evaluate model
        score = model.score(X_test, y_test)
        logger.info(f"Gradient Boosting R² score: {score:.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training Gradient Boosting model: {e}")
        raise


def prepare_features(data):
    """
    Prepare features for tree-based models.
    
    Args:
        data (DataFrame): DataFrame with timestamp and base_fee_gwei
        
    Returns:
        DataFrame: DataFrame with engineered features
    """
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Create lag features
    for lag in [1, 3, 6, 12, 24]:
        df[f'lag_{lag}'] = df['base_fee_gwei'].shift(lag)
    
    # Create rolling statistics
    for window in [6, 12, 24, 48]:
        df[f'rolling_mean_{window}'] = df['base_fee_gwei'].rolling(window=window).mean()
        df[f'rolling_std_{window}'] = df['base_fee_gwei'].rolling(window=window).std()
        df[f'rolling_min_{window}'] = df['base_fee_gwei'].rolling(window=window).min()
        df[f'rolling_max_{window}'] = df['base_fee_gwei'].rolling(window=window).max()
    
    # Drop rows with NaN values
    df = df.dropna()
    
    # Drop timestamp and target columns for features
    features = df.drop(['timestamp', 'base_fee_gwei'], axis=1)
    
    return features
