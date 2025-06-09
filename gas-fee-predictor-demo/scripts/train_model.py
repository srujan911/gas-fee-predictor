

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import joblib
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_and_preprocess_data(data_path="data/gas_fees_cleaned.csv"):
    """Load and preprocess the gas fee data."""
    try:
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded data shape: {df.shape}")
        logger.info("Converting timestamp to unix format")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df = df.dropna(subset=["timestamp"])
        df["timestamp"] = df["timestamp"].map(lambda x: int(x.timestamp()))
        df["block_number"] = df["block_number"].astype(int)
        for col in ["gas_used", "gas_limit", "tx_count"]:
            if col in df.columns:
                df[col] = df[col].astype(int)

        required_columns = ["timestamp", "block_number", "gas_used", "gas_limit", "tx_count", "base_fee_gwei"]
        logger.info("Dropping rows with missing values in key columns")
        df = df.dropna(subset=required_columns)

        X = df[["timestamp", "block_number", "gas_used", "gas_limit", "tx_count"]]
        y = df["base_fee_gwei"]

        logger.info(f"Preprocessed data shape: X={X.shape}, y={y.shape}")
        return X, y, df
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}")
        raise

def scale_features(X):
    """Scale the features using StandardScaler."""
    try:
        logger.info("Scaling features")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        logger.info("Features scaled successfully")
        return X_scaled, scaler
    except Exception as e:
        logger.error(f"Error in feature scaling: {e}")
        raise

def train_model(X_train, y_train, perform_grid_search=False):
    """Train the XGBoost regression model."""
    try:
        if perform_grid_search:
            logger.info("Performing grid search for hyperparameter tuning")
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 6, 9],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0]
            }
            model = XGBRegressor(objective='reg:squarederror')
            grid_search = GridSearchCV(model, param_grid, cv=3, scoring='neg_mean_absolute_error')
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            logger.info(f"Best parameters: {grid_search.best_params_}")
            return best_model
        else:
            logger.info("Training XGBoost model with default parameters")
            model = XGBRegressor(
                objective='reg:squarederror',
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            model.fit(X_train, y_train)
            logger.info("Model training completed")
            return model
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise

def evaluate_model(model, X_test, y_test):
    """Evaluate the trained model."""
    try:
        logger.info("Evaluating model performance")
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        logger.info(f"Model evaluation metrics:")
        logger.info(f"Mean Absolute Error: {mae:.2f} GWEI")
        logger.info(f"Root Mean Squared Error: {rmse:.2f} GWEI")
        logger.info(f"R² Score: {r2:.4f}")

        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'predictions': y_pred
        }
    except Exception as e:
        logger.error(f"Error in model evaluation: {e}")
        raise

def save_model(model, scaler, metrics, output_path="models/gas_fee_model.pkl"):
    """Save the trained model and scaler."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Saving model to {output_path}")
        joblib.dump((model, scaler), output_path)
        metrics_path = os.path.join(os.path.dirname(output_path), "model_metrics.txt")
        with open(metrics_path, 'w') as f:
            f.write(f"Model Training Results\n")
            f.write(f"=====================\n")
            f.write(f"Mean Absolute Error: {metrics['mae']:.2f} GWEI\n")
            f.write(f"Root Mean Squared Error: {metrics['rmse']:.2f} GWEI\n")
            f.write(f"R² Score: {metrics['r2']:.4f}\n")
            f.write(f"\nTraining Date: {pd.Timestamp.now()}\n")
            f.write(f"\nFeature Importance Explanation\n")
            f.write(f"===========================\n")
            f.write(f"Feature importance values show the relative importance of each feature\n")
            f.write(f"in making predictions. Values are on a scale from 0 to 1, where higher\n")
            f.write(f"values indicate greater importance. The sum of all importance values equals 1.\n")
            f.write(f"These are NOT the actual values of the features but their relative importance\n")
            f.write(f"in the prediction model.\n")

        logger.info(f"Model and metrics saved successfully")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise

def plot_feature_importance(model, feature_names):
    """Plot feature importance from the trained model."""
    try:
        importance = model.feature_importances_
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importance
        }).sort_values('Importance', ascending=False)
        feature_importance['Percentage'] = feature_importance['Importance'] * 100
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='Importance', y='Feature', data=feature_importance)
        for i, p in enumerate(ax.patches):
            width = p.get_width()
            plt.text(width + 0.01, p.get_y() + p.get_height()/2,
                    f'{feature_importance.iloc[i]["Percentage"]:.2f}%',
                    ha='left', va='center')

        plt.title('Feature Importance for Gas Fee Prediction', fontsize=16)
        plt.xlabel('Relative Importance (0-1 scale)', fontsize=12)
        plt.tight_layout()
        os.makedirs('models/plots', exist_ok=True)
        plt.savefig('models/plots/feature_importance.png')
        logger.info("Feature importance plot saved to models/plots/feature_importance.png")
        return feature_importance
    except Exception as e:
        logger.error(f"Error plotting feature importance: {e}")
        logger.info("Continuing without plotting feature importance")
        return None

def train_gas_fee_model():
    """Function to train the gas fee model for the pipeline."""
    try:
        logger.info("Starting gas fee model training")
        X, y, _ = load_and_preprocess_data() 
        X_scaled, scaler = scale_features(X)
        logger.info("Splitting data into training and testing sets")
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        model = train_model(X_train, y_train, perform_grid_search=False)
        metrics = evaluate_model(model, X_test, y_test)
        feature_importance = plot_feature_importance(model, X.columns)
        save_model(model, scaler, metrics)
        logger.info("Gas fee model training completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error training gas fee model: {e}")
        return False

def main():
    """Main function to run the model training pipeline."""
    try:
        success = train_gas_fee_model()

        if success:
            print("\n" + "=" * 50)
            print("🔮 ETHEREUM GAS FEE PREDICTION MODEL 🔮")
            print("=" * 50)
            print(f"✅ Model trained successfully with XGBoost!")
            metrics_path = "models/model_metrics.txt"
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    metrics_content = f.read()
                    print(metrics_content)

            print("=" * 50)
            return 0
        else:
            print("❌ Model training failed")
            return 1
    except Exception as e:
        logger.error(f"An error occurred in the training pipeline: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
