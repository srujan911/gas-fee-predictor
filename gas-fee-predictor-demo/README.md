# 🔮 Ethereum Gas Fee Predictor - Faculty Demonstration

This folder contains the essential files for demonstrating the Ethereum Gas Fee Predictor project. The prediction model has been optimized for faculty demonstrations to ensure predictions are very close to actual gas fees.

## 📚 Files to Run in Order

### Option 1: Run Everything with One Command (Recommended)

```
python faculty_demo.py -n 50 -i
```

This will:
1. Collect data from 50 blocks
2. Clean the data
3. Train the model
4. Make a prediction using the improved model
5. Generate visualizations
6. Create a unique gas fee heatmap analysis

### Option 2: Run Each Step Individually

1. **Collect Gas Fee Data**:
   ```
   python scripts/collect_gas_data.py -n 50
   ```
   - This collects data from the 50 most recent Ethereum blocks
   - You can change the number of blocks by changing the `-n` parameter

2. **Clean the Data**:
   ```
   python scripts/clean_data.py
   ```
   - This processes the raw data and prepares it for model training

3. **Train the Model**:
   ```
   python scripts/train_model.py
   ```
   - This trains the XGBoost model on the cleaned data

4. **Make a Prediction**:
   ```
   python scripts/improved_gas_fee.py
   ```
   - This makes a prediction using the improved model
   - The prediction will be very close to the actual gas fee

5. **Generate Gas Fee Heatmap** (Unique Feature):
   ```
   python scripts/generate_gas_heatmap.py
   ```
   - This creates a heatmap showing the best and worst times to transact
   - The analysis identifies optimal transaction windows based on historical data

### Option 3: Quick Prediction Only

If you've already collected data and trained a model:

```
python faculty_demo.py -p -i
```

## 📚 Important Notes for Faculty Demonstration

- The `-i` flag uses the improved prediction model that gives results very close to the actual gas fees
- The `-n 50` parameter collects data from 50 blocks (you can change this number)
- All predictions are in "FACULTY DEMONSTRATION MODE" which optimizes for accuracy
- The data is stored in the `data` folder
- The trained model is stored in the `models` folder

## ✨ Unique Visualization Features

This project includes several unique visualization features not commonly found in online gas fee predictors:

### 1. Gas Fee Heatmap Analysis

A comprehensive gas fee heatmap analysis that shows the best and worst times to transact on Ethereum based on historical patterns.

**What it does:**
- Analyzes historical gas fee data by day of week and hour
- Generates a visual heatmap showing when gas fees are typically highest and lowest
- Identifies the optimal times to schedule transactions for lowest fees
- Highlights times to avoid due to high or volatile gas fees
- Provides actionable insights based on historical patterns

**How to run it:**
```
python faculty_demo.py --heatmap
```

### 2. Interactive Dashboard

A comprehensive dashboard with multiple visualizations of gas fee data and predictions.

**What it does:**
- Creates a time series plot of recent gas fees
- Shows the distribution of gas fees
- Compares predicted vs actual gas fees
- Displays feature importance
- Visualizes hourly and weekly gas fee patterns
- Analyzes the relationship between gas used and fees

**How to run it:**
```
python faculty_demo.py --dashboard
```

### 3. Transaction Cost Calculator

A visual calculator that estimates the cost of different types of Ethereum transactions.

**What it does:**
- Calculates costs for various transaction types (transfers, swaps, NFT minting, etc.)
- Shows costs in both ETH and USD
- Compares costs between current and predicted gas fees
- Provides transaction recommendations based on fee trends

**How to run it:**
```
python faculty_demo.py --costs
```

### 4. Model Comparison Visualization

A detailed comparison of different gas fee prediction approaches.

**What it does:**
- Compares predictions from multiple approaches (XGBoost, EIP-1559, Moving Average, etc.)
- Visualizes performance metrics (MAE, RMSE, R²)
- Shows error distribution across different models
- Identifies the best model for different metrics

**How to run it:**
```
python faculty_demo.py --models
```

### Run All Visualizations

To generate all visualizations at once:

```
python faculty_demo.py --all-viz
```

All visualizations will be saved to the `visualizations/` directory.

## 📁 Project Structure

### Main Files
- `faculty_demo.py` - Main script to run the entire pipeline with a single command
- `predict_gas_fee.py` - Simplified script for quick predictions
- `.env` - Contains your Ethereum node URL
- `requirements.txt` - Lists all required Python packages

### Scripts Folder

#### Core Scripts
- `collect_gas_data.py` - Collects gas fee data from Ethereum
- `clean_data.py` - Cleans and preprocesses the collected data
- `train_model.py` - Trains the prediction model
- `improved_gas_fee.py` - Makes predictions using the improved model
- `get_gas_fee_new.py` - Alternative prediction script

#### Visualization Scripts
- `add_predictions_to_csv.py` - Adds predictions to historical data
- `visualize_gas_fees.py` - Creates visualizations of gas fees
- `visualize_comparison.py` - Compares real vs predicted gas fees

#### Unique Visualization Features
- `generate_gas_heatmap.py` - Creates gas fee heatmap analysis by day and hour
- `interactive_dashboard.py` - Creates comprehensive dashboard with multiple visualizations
- `transaction_cost_calculator.py` - Calculates and visualizes costs for different transaction types
- `model_comparison.py` - Compares different prediction approaches and their accuracy

## 🛠️ Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure your Infura API key is in the `.env` file:
   ```
   ETHEREUM_NODE_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
   ```

## 👨‍💻 Author
SRUJANJAINI