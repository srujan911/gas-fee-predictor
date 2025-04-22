# 🔮 Ethereum Gas Fee Predictor

This project uses live Ethereum blockchain data to predict future gas fees using machine learning techniques. By analyzing historical gas fee patterns, the model can forecast upcoming gas prices to help users optimize transaction timing and costs.

## 📦 Features
- Connects to Ethereum mainnet using Infura API
- Collects and processes real-time gas fee data
- Cleans and prepares data for machine learning
- Trains an XGBoost regression model with feature scaling
- Predicts future gas fees based on multiple blockchain metrics
- Visualizes historical and predicted gas fees with interactive charts
- Detects anomalies in gas fee predictions

## 📁 Project Structure
- `data/`: Collected and processed gas fee data
  - `gas_fees.csv`: Raw collected data
  - `gas_fees_cleaned.csv`: Processed data ready for training
  - `gas_fees_with_predictions.csv`: Data with model predictions
  - `rolling_gas_stats.csv`: Rolling statistics for anomaly detection
- `models/`: Trained machine learning models
  - `gas_fee_model.pkl`: Serialized XGBoost model with scaler
- `scripts/`: Python scripts for different project components
  - `collect_gas_data.py`: Fetches blockchain data
  - `clean_data.py`: Preprocesses the collected data
  - `train_model.py`: Trains the XGBoost model
  - `predict_gas_fee.py`: Makes predictions using the trained model
  - `get_gas_fee.py`: Gets current gas fee from Ethereum
  - `add_predictions_to_csv.py`: Adds predictions to historical data
  - `visualize_gas_fees.py`: Creates interactive visualizations
  - `visualize_comparison.py`: Compares real vs predicted fees
  - `animate_time_series.py`: Creates animated time series visualization
- `predict_gas_fee.py`: Main script for quick gas fee prediction
- `test_env.py`: Tests Ethereum connection

## 🛠️ Setup and Installation
1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set your Infura API key in the `.env` file:
   ```
   ETHEREUM_NODE_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
   ```

## 🚀 Usage
1. Collect gas fee data:
   ```
   python scripts/collect_gas_data.py
   ```
2. Clean the collected data:
   ```
   python scripts/clean_data.py
   ```
3. Train the prediction model:
   ```
   python scripts/train_model.py
   ```
4. Make predictions:
   ```
   python scripts/predict_gas_fee.py
   ```
5. Visualize the results:
   ```
   python scripts/visualize_comparison.py
   ```

## 📊 Visualization Examples
- Time series plots of gas fees over time
- Hourly gas fee patterns
- Comparison between predicted and actual gas fees
- Animated visualizations of gas fee trends

## 🧪 Model Performance
The XGBoost regression model achieves a Mean Absolute Error (MAE) of approximately 2-3 GWEI on test data, making it suitable for practical gas fee prediction applications.

## 🔍 Future Improvements
- Implement more advanced time series models (ARIMA, Prophet)
- Add real-time prediction API endpoint
- Incorporate more blockchain metrics as features
- Develop a web interface for easy interaction
- Extend to other blockchain networks

## 📝 License
MIT

## 👨‍💻 Author
SRUJANJAINI