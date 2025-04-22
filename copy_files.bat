@echo off
echo Copying essential files to gas-fee-predictor-demo folder...

REM Copy script files
copy scripts\collect_gas_data.py gas-fee-predictor-demo\scripts\
copy scripts\clean_data.py gas-fee-predictor-demo\scripts\
copy scripts\train_model.py gas-fee-predictor-demo\scripts\
copy scripts\improved_gas_fee.py gas-fee-predictor-demo\scripts\
copy scripts\get_gas_fee_new.py gas-fee-predictor-demo\scripts\
copy scripts\add_predictions_to_csv.py gas-fee-predictor-demo\scripts\
copy scripts\visualize_gas_fees.py gas-fee-predictor-demo\scripts\
copy scripts\visualize_comparison.py gas-fee-predictor-demo\scripts\

REM Copy main files
copy faculty_demo.py gas-fee-predictor-demo\
copy predict_gas_fee.py gas-fee-predictor-demo\
copy requirements.txt gas-fee-predictor-demo\
copy .env gas-fee-predictor-demo\
copy README.md gas-fee-predictor-demo\

echo Files copied successfully!
