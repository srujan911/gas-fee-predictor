# Ethereum Gas Fee Predictor - Web Frontend

This document provides instructions for setting up and running the web frontend for the Ethereum Gas Fee Predictor project.

## Overview

The web frontend provides a user-friendly interface for interacting with the Ethereum Gas Fee Predictor. It includes:

- Real-time gas fee predictions
- Interactive visualizations
- Gas fee heatmap analysis
- Transaction cost calculator
- Pipeline execution interface

## Prerequisites

Before running the frontend, make sure you have installed all the required dependencies:

```
pip install -r requirements.txt
```

## Running the Frontend

To start the web frontend, run the following command from the project directory:

```
python app.py
```

This will start a Flask development server on `http://127.0.0.1:5000/`. Open this URL in your web browser to access the frontend.

## Features

### Dashboard

The main dashboard displays:
- Current gas fee from the latest Ethereum block
- Predicted gas fee for the next block
- Block statistics (gas used, gas limit, transaction count)
- Historical gas fee chart

### Gas Fee Predictions

This section provides:
- Hourly gas fee patterns
- Prediction accuracy metrics
- Trend analysis and transaction recommendations

### Gas Fee Heatmap

The heatmap analysis shows:
- Gas fee patterns by day of week and hour
- Best and worst times to transact
- Recommended transaction windows

### Transaction Cost Calculator

The calculator provides:
- Cost estimates for different transaction types
- Comparison between current and predicted costs
- Potential savings based on gas fee predictions

### Pipeline Execution

This section allows you to:
- Run the full prediction pipeline
- Configure the number of blocks to collect
- Choose between standard and improved prediction models

## For Faculty Demonstration

For your faculty demonstration, the web frontend provides a comprehensive and visually appealing way to showcase your project. It demonstrates:

1. **Real-time Data Integration**: Shows how your project connects to the Ethereum blockchain
2. **Prediction Capabilities**: Displays gas fee predictions with accuracy metrics
3. **Data Visualization**: Presents multiple interactive visualizations
4. **Practical Applications**: Demonstrates real-world use cases through the transaction cost calculator
5. **Unique Features**: Showcases the gas fee heatmap analysis

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly
2. Check that your Ethereum node URL is correctly set in the `.env` file
3. Ensure you have an internet connection to access the Ethereum network
4. Check the console for any error messages

## Customization

You can customize the frontend by modifying:
- `templates/index.html` - HTML structure
- `static/css/style.css` - Visual styling
- `static/js/main.js` - Frontend functionality
- `app.py` - Backend API endpoints
