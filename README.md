# 🔮 Ethereum Gas Fee Predictor

This project uses live Ethereum data to predict future gas fees using machine learning.

## 📦 Features
- Connects to Ethereum using Infura
- Collects real-time gas fee data
- Trains a Linear Regression model
- Predicts future gas fees based on timestamp and block number

## 📁 Structure
- `data/`: Collected gas data
- `models/`: Trained ML model
- `scripts/`: Code for data collection, training, and prediction

## 🛠️ Setup
1. Clone the repo
2. Install dependencies:
3. Set your Infura node URL in each script
4. Run scripts in order:
- `collect_gas_data.py`
- `train_model.py`
- `predict_gas_fee.py`

## ✅ Example Output
📦 Block Number: 22199721 🕒 Timestamp: 2025-04-05 07:55:57 🔮 Predicted Base Fee: 55.01 GWEI