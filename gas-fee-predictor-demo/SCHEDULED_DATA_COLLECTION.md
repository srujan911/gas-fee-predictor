# Scheduled Data Collection for Ethereum Gas Fee Predictor

This document provides instructions for setting up scheduled data collection for the Ethereum Gas Fee Predictor project.

## Overview

To improve the accuracy of gas fee predictions, the system needs to collect historical gas fee data regularly. This document explains how to set up automated data collection at regular intervals.

## Requirements

- Python 3.8 or higher
- Access to an Ethereum node (local or remote)
- API keys for gas fee data sources (optional but recommended)
- Task scheduler (Windows Task Scheduler, cron, etc.)

## Data Collection Script

The main data collection script is `scripts/get_gas_fee_new.py`. This script fetches gas fee data from multiple sources and saves it to a CSV file.

### Script Options

```
python scripts/get_gas_fee_new.py --help
```

Available options:
- `--output`: Path to output CSV file (default: `data/historical_gas_data.csv`)
- `--etherscan-key`: Etherscan API key
- `--ethgasstation-key`: ETH Gas Station API key
- `--provider-url`: Ethereum node provider URL
- `--gasnow-key`: GasNow API key
- `--interval`: Interval in seconds for continuous data collection (0 for single run)

### Example Usage

```
python scripts/get_gas_fee_new.py --output data/historical_gas_data.csv --etherscan-key YOUR_ETHERSCAN_KEY --provider-url https://mainnet.infura.io/v3/YOUR_INFURA_KEY
```

## Setting Up Scheduled Collection

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Click "Create Basic Task"
3. Enter a name (e.g., "Ethereum Gas Fee Data Collection")
4. Select "Daily" or your preferred schedule
5. Set the start time and recurrence
6. Select "Start a program"
7. Browse to your Python executable
8. Add the script path and arguments in "Add arguments":
   ```
   C:\path\to\gas-fee-predictor-demo\scripts\get_gas_fee_new.py --etherscan-key YOUR_KEY
   ```
9. Set the "Start in" field to your project directory:
   ```
   C:\path\to\gas-fee-predictor-demo
   ```
10. Complete the wizard and check "Open the Properties dialog"
11. In the Properties dialog, go to the "Settings" tab
12. Check "Run task as soon as possible after a scheduled start is missed"
13. Click "OK" to save

### Linux/macOS (cron)

1. Open your crontab file:
   ```
   crontab -e
   ```

2. Add a line to run the script at your desired interval:
   ```
   # Run every hour
   0 * * * * cd /path/to/gas-fee-predictor-demo && /usr/bin/python3 scripts/get_gas_fee_new.py --etherscan-key YOUR_KEY
   ```

3. Save and exit

## Continuous Collection Mode

For development or testing, you can run the script in continuous mode:

```
python scripts/get_gas_fee_new.py --interval 3600
```

This will collect data every 3600 seconds (1 hour) until the script is stopped.

## Data Storage Considerations

### File Size Management

The historical gas data CSV file will grow over time. Consider implementing a rotation strategy:

1. Create a new file each month:
   ```
   python scripts/get_gas_fee_new.py --output data/historical_gas_data_$(date +%Y%m).csv
   ```

2. Or use the `--max-records` option to limit the number of records:
   ```
   python scripts/get_gas_fee_new.py --max-records 10000
   ```

### Database Storage

For production use, consider storing data in a database instead of CSV files:

1. Set up a database (SQLite, PostgreSQL, etc.)
2. Modify the script to store data in the database
3. Implement data retention policies

## Monitoring Collection

To ensure data collection is working properly:

1. Set up logging:
   ```
   python scripts/get_gas_fee_new.py --log-file logs/collection.log
   ```

2. Create a monitoring script to check for gaps in data:
   ```
   python scripts/monitor_data_collection.py
   ```

3. Set up alerts for collection failures

## Troubleshooting

### Common Issues

1. **API Rate Limits**: If you hit rate limits, increase the collection interval or use multiple API keys.

2. **Network Errors**: Implement retry logic for network failures.

3. **Disk Space**: Monitor disk space usage, especially for long-term collection.

4. **Process Hanging**: Set up a watchdog to restart the process if it hangs.

## Data Processing

After collection, you may want to process the data:

1. Clean and normalize the data:
   ```
   python scripts/clean_data.py
   ```

2. Generate visualizations:
   ```
   python scripts/visualize_gas_fees.py
   ```

3. Train prediction models:
   ```
   python scripts/train_model.py
   ```

## Conclusion

Regular data collection is essential for accurate gas fee predictions. By setting up scheduled collection, you ensure that your prediction models have access to the latest data and can adapt to changing network conditions.
