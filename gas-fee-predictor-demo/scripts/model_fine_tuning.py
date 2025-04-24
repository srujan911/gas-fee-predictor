"""
Model Fine-Tuning for Ethereum Gas Fee Prediction

This script performs hyperparameter tuning for the best-performing model
to optimize its performance for gas fee prediction.

Author: SRUJANJAINI
Date: April 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, make_scorer
from sklearn.preprocessing import StandardScaler
import joblib
import xgboost as xgb
import lightgbm as lgb
from datetime import datetime, timedelta

def load_enhanced_data(file_path='data/enhanced_gas_data.csv'):
    """
    Load enhanced gas fee data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing enhanced gas fee data
        
    Returns:
        DataFrame containing enhanced gas fee data
    """
    try:
        if not os.path.exists(file_path):
            print(f"Warning: Enhanced data file not found at {file_path}")
            return None
            
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime if it's not already
        if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        print(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading enhanced data: {e}")
        return None

def prepare_features(df, target_col=None, exclude_cols=None):
    """
    Prepare features and target for model training.
    
    Args:
        df: DataFrame containing enhanced gas fee data
        target_col: Column name for target variable (if None, will try to detect)
        exclude_cols: List of columns to exclude from features
        
    Returns:
        Tuple of (X, y, feature_names)
    """
    try:
        if df is None or len(df) == 0:
            print("No data available for feature preparation")
            return None, None, None
            
        # Ensure target column exists
        if target_col is None:
            for col in ['gas_fee', 'base_fee_gwei']:
                if col in df.columns:
                    target_col = col
                    break
                    
        if target_col is None:
            print("Target column not found in data")
            return None, None, None
            
        # Default exclude columns
        if exclude_cols is None:
            exclude_cols = ['timestamp', 'block_number', 'day_name', 'time_of_day', target_col]
            
        # Add any columns with the target name in them to exclude list
        for col in df.columns:
            if target_col in col and col != target_col:
                exclude_cols.append(col)
                
        # Get feature columns
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Handle categorical columns
        df_processed = df.copy()
        for col in feature_cols:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                # One-hot encode categorical columns
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df_processed = pd.concat([df_processed, dummies], axis=1)
                feature_cols.remove(col)
                feature_cols.extend(dummies.columns.tolist())
                
        # Prepare features and target
        X = df_processed[feature_cols].fillna(0)
        y = df_processed[target_col]
        
        print(f"Prepared {len(feature_cols)} features for model training")
        return X, y, feature_cols
    except Exception as e:
        print(f"Error preparing features: {e}")
        return None, None, None

def tune_xgboost(X, y, output_dir='models'):
    """
    Perform hyperparameter tuning for XGBoost model.
    
    Args:
        X: Feature matrix
        y: Target vector
        output_dir: Directory to save model files
        
    Returns:
        Tuple of (best_model, best_params, cv_results)
    """
    try:
        if X is None or y is None:
            print("No data available for model tuning")
            return None, None, None
            
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save scaler
        joblib.dump(scaler, os.path.join(output_dir, 'xgboost_scaler.pkl'))
        
        # Define parameter grid for XGBoost
        param_grid = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [3, 4, 5, 6, 7],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0],
            'gamma': [0, 0.1, 0.2],
            'min_child_weight': [1, 3, 5]
        }
        
        # Define custom scorer (negative MAE because GridSearchCV maximizes score)
        mae_scorer = make_scorer(mean_absolute_error, greater_is_better=False)
        
        # Initialize XGBoost model
        xgb_model = xgb.XGBRegressor(random_state=42)
        
        # Perform randomized search (faster than grid search for many parameters)
        print("Performing RandomizedSearchCV for XGBoost...")
        random_search = RandomizedSearchCV(
            estimator=xgb_model,
            param_distributions=param_grid,
            n_iter=50,  # Number of parameter settings to try
            scoring=mae_scorer,
            cv=5,
            verbose=1,
            random_state=42,
            n_jobs=-1
        )
        
        # Fit randomized search
        random_search.fit(X_train_scaled, y_train)
        
        # Get best parameters
        best_params = random_search.best_params_
        print(f"Best parameters: {best_params}")
        
        # Train model with best parameters
        best_model = xgb.XGBRegressor(**best_params, random_state=42)
        best_model.fit(X_train_scaled, y_train)
        
        # Evaluate on test set
        y_pred = best_model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        print(f"Test MAE: {mae:.4f}, Test RMSE: {rmse:.4f}, Test R2: {r2:.4f}, Test MAPE: {mape:.4f}")
        
        # Save best model
        joblib.dump(best_model, os.path.join(output_dir, 'xgboost_tuned.pkl'))
        
        # Save CV results
        cv_results = pd.DataFrame(random_search.cv_results_)
        cv_results.to_csv(os.path.join(output_dir, 'xgboost_cv_results.csv'), index=False)
        
        # Plot learning curve
        plt.figure(figsize=(10, 6))
        plt.plot(best_model.evals_result()['validation_0']['mae'])
        plt.title('XGBoost Learning Curve')
        plt.xlabel('Boosting Round')
        plt.ylabel('MAE')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'xgboost_learning_curve.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot feature importances
        feature_importances = pd.DataFrame({
            'Feature': X.columns,
            'Importance': best_model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Importance', y='Feature', data=feature_importances.head(20))
        plt.title('XGBoost Feature Importances (Top 20)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'xgboost_feature_importances.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save feature importances
        feature_importances.to_csv(os.path.join(output_dir, 'xgboost_feature_importances.csv'), index=False)
        
        print("XGBoost tuning completed successfully")
        return best_model, best_params, cv_results
    except Exception as e:
        print(f"Error tuning XGBoost: {e}")
        return None, None, None

def tune_lightgbm(X, y, output_dir='models'):
    """
    Perform hyperparameter tuning for LightGBM model.
    
    Args:
        X: Feature matrix
        y: Target vector
        output_dir: Directory to save model files
        
    Returns:
        Tuple of (best_model, best_params, cv_results)
    """
    try:
        if X is None or y is None:
            print("No data available for model tuning")
            return None, None, None
            
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save scaler
        joblib.dump(scaler, os.path.join(output_dir, 'lightgbm_scaler.pkl'))
        
        # Define parameter grid for LightGBM
        param_grid = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [3, 4, 5, 6, 7, -1],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'num_leaves': [31, 50, 70, 90],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0],
            'min_child_samples': [5, 10, 20, 30]
        }
        
        # Define custom scorer (negative MAE because GridSearchCV maximizes score)
        mae_scorer = make_scorer(mean_absolute_error, greater_is_better=False)
        
        # Initialize LightGBM model
        lgb_model = lgb.LGBMRegressor(random_state=42)
        
        # Perform randomized search (faster than grid search for many parameters)
        print("Performing RandomizedSearchCV for LightGBM...")
        random_search = RandomizedSearchCV(
            estimator=lgb_model,
            param_distributions=param_grid,
            n_iter=50,  # Number of parameter settings to try
            scoring=mae_scorer,
            cv=5,
            verbose=1,
            random_state=42,
            n_jobs=-1
        )
        
        # Fit randomized search
        random_search.fit(X_train_scaled, y_train)
        
        # Get best parameters
        best_params = random_search.best_params_
        print(f"Best parameters: {best_params}")
        
        # Train model with best parameters
        best_model = lgb.LGBMRegressor(**best_params, random_state=42)
        best_model.fit(X_train_scaled, y_train)
        
        # Evaluate on test set
        y_pred = best_model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        print(f"Test MAE: {mae:.4f}, Test RMSE: {rmse:.4f}, Test R2: {r2:.4f}, Test MAPE: {mape:.4f}")
        
        # Save best model
        joblib.dump(best_model, os.path.join(output_dir, 'lightgbm_tuned.pkl'))
        
        # Save CV results
        cv_results = pd.DataFrame(random_search.cv_results_)
        cv_results.to_csv(os.path.join(output_dir, 'lightgbm_cv_results.csv'), index=False)
        
        # Plot feature importances
        feature_importances = pd.DataFrame({
            'Feature': X.columns,
            'Importance': best_model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Importance', y='Feature', data=feature_importances.head(20))
        plt.title('LightGBM Feature Importances (Top 20)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'lightgbm_feature_importances.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save feature importances
        feature_importances.to_csv(os.path.join(output_dir, 'lightgbm_feature_importances.csv'), index=False)
        
        print("LightGBM tuning completed successfully")
        return best_model, best_params, cv_results
    except Exception as e:
        print(f"Error tuning LightGBM: {e}")
        return None, None, None

def create_ensemble_model(X, y, models, output_dir='models'):
    """
    Create an ensemble model by averaging predictions from multiple models.
    
    Args:
        X: Feature matrix
        y: Target vector
        models: List of tuples (model_name, model_object)
        output_dir: Directory to save model files
        
    Returns:
        Dictionary containing ensemble model evaluation results
    """
    try:
        if X is None or y is None or not models:
            print("No data or models available for ensemble creation")
            return None
            
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save scaler
        joblib.dump(scaler, os.path.join(output_dir, 'ensemble_scaler.pkl'))
        
        # Get predictions from each model
        predictions = []
        model_names = []
        
        for model_name, model in models:
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            predictions.append(y_pred)
            model_names.append(model_name)
            
            # Calculate metrics for individual model
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            
            print(f"{model_name} - Test MAE: {mae:.4f}, Test RMSE: {rmse:.4f}, Test R2: {r2:.4f}, Test MAPE: {mape:.4f}")
            
        # Create ensemble prediction (simple average)
        ensemble_pred = np.mean(predictions, axis=0)
        
        # Calculate metrics for ensemble
        ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
        ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
        ensemble_r2 = r2_score(y_test, ensemble_pred)
        ensemble_mape = np.mean(np.abs((y_test - ensemble_pred) / y_test)) * 100
        
        print(f"Ensemble - Test MAE: {ensemble_mae:.4f}, Test RMSE: {ensemble_rmse:.4f}, Test R2: {ensemble_r2:.4f}, Test MAPE: {ensemble_mape:.4f}")
        
        # Save ensemble model information
        ensemble_info = {
            'model_names': model_names,
            'metrics': {
                'mae': ensemble_mae,
                'rmse': ensemble_rmse,
                'r2': ensemble_r2,
                'mape': ensemble_mape
            }
        }
        
        # Save ensemble info
        with open(os.path.join(output_dir, 'ensemble_info.json'), 'w') as f:
            json.dump(ensemble_info, f, indent=4)
            
        # Plot predictions comparison
        plt.figure(figsize=(14, 8))
        
        # Plot actual values
        plt.plot(y_test.values, label='Actual', color='black', linewidth=2)
        
        # Plot predictions for each model
        for i, model_name in enumerate(model_names):
            plt.plot(predictions[i], label=model_name, alpha=0.5)
            
        # Plot ensemble prediction
        plt.plot(ensemble_pred, label='Ensemble', color='red', linewidth=2)
        
        plt.title('Model Predictions Comparison')
        plt.xlabel('Sample Index')
        plt.ylabel('Gas Fee (GWEI)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'ensemble_predictions.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Ensemble model creation completed successfully")
        return ensemble_info
    except Exception as e:
        print(f"Error creating ensemble model: {e}")
        return None

def main():
    """Main function to run the model fine-tuning pipeline."""
    try:
        # Load enhanced data
        df = load_enhanced_data()
        
        if df is None:
            print("No enhanced data available. Please run data_enhancements.py first.")
            return
            
        # Prepare features
        X, y, feature_names = prepare_features(df)
        
        if X is None or y is None:
            print("Failed to prepare features. Exiting.")
            return
            
        # Tune XGBoost model
        xgb_model, xgb_params, xgb_cv_results = tune_xgboost(X, y)
        
        # Tune LightGBM model
        lgb_model, lgb_params, lgb_cv_results = tune_lightgbm(X, y)
        
        # Create ensemble model
        if xgb_model is not None and lgb_model is not None:
            models = [
                ('XGBoost', xgb_model),
                ('LightGBM', lgb_model)
            ]
            
            ensemble_info = create_ensemble_model(X, y, models)
            
        print("Model fine-tuning completed successfully.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
