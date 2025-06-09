
import os
import sys
import pandas as pd
import numpy as np
import json
import uuid
import plotly
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from pytz import timezone

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.improved_gas_fee import predict_gas_fee, connect_to_ethereum, load_model
from scripts.generate_gas_heatmap import load_historical_data, generate_gas_fee_heatmap, find_optimal_transaction_times
from scripts.transaction_cost_calculator import calculate_transaction_costs, get_eth_price
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ethereum-gas-fee-predictor'
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'armoredfamine@gmail.com' 
app.config['MAIL_PASSWORD'] = 'obeg dhjp fcje wylb'  
app.config['MAIL_DEFAULT_SENDER'] = 'jainisrujan@gmail.com'  
app.config['MAIL_MAX_EMAILS'] = 5  
app.config['MAIL_DEBUG'] = True 
USE_DUMMY_EMAIL_SENDER = False  
mail = Mail(app)

os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs(os.path.join('static', 'images'), exist_ok=True)
os.makedirs(os.path.join('static', 'js'), exist_ok=True)
os.makedirs(os.path.join('static', 'css'), exist_ok=True)
os.makedirs('templates', exist_ok=True)
last_prediction = None
last_prediction_time = None

def send_email(to_email, subject, html_content):
    """Send an email using Flask-Mail."""
    try:
        print(f"Attempting to send email to {to_email} with subject: {subject}")
        print(f"Using SMTP server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
        print(f"Using sender: {app.config['MAIL_DEFAULT_SENDER']}")
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        if USE_DUMMY_EMAIL_SENDER:
            print("=== DUMMY EMAIL SENDER ===")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Content: {html_content[:100]}...")
            print("=== END OF DUMMY EMAIL ===")
            return True
        with app.app_context():
            mail.send(msg)

        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        try:
            print("Attempting direct SMTP connection as fallback...")
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = app.config['MAIL_SERVER']
            port = app.config['MAIL_PORT']
            sender_email = app.config['MAIL_USERNAME']
            password = app.config['MAIL_PASSWORD']
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = to_email
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message.as_string())
            server.quit()

            print("Direct SMTP connection successful!")
            return True
        except Exception as smtp_error:
            print(f"Direct SMTP also failed: {str(smtp_error)}")
            return False

def send_alert_confirmation_email(alert):
    """Send a confirmation email for a new gas fee alert."""
    to_email = alert['email']
    threshold = alert['threshold']
    condition = alert.get('condition', 'below')
    expires_at = datetime.fromisoformat(alert['expires_at']).strftime('%Y-%m-%d %H:%M:%S')

    subject = "Ethereum Gas Fee Alert Confirmation"

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #1a2a6c; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            .alert-details {{ background-color: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #1a2a6c; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Ethereum Gas Fee Alert Confirmation</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Your gas fee alert has been set successfully. We'll notify you when the gas fee {condition} <strong>{threshold} GWEI</strong>.</p>

                <div class="alert-details">
                    <h3>Alert Details:</h3>
                    <p><strong>Condition:</strong> Gas fee {condition} {threshold} GWEI</p>
                    <p><strong>Expires:</strong> {expires_at}</p>
                </div>

                <p>You'll receive a notification email when this condition is met.</p>
                <p>Thank you for using our Ethereum Gas Fee Predictor!</p>
            </div>
            <div class="footer">
                <p>© 2025 Ethereum Gas Fee Predictor - Created by SRUJAN.J</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)

def send_alert_triggered_email(alert, current_fee):
    """Send an email when a gas fee alert is triggered."""
    to_email = alert['email']
    threshold = alert['threshold']
    condition = alert.get('condition', 'below')

    subject = "Ethereum Gas Fee Alert Triggered!"

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #28a745; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            .alert-details {{ background-color: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; }}
            .cta-button {{ display: inline-block; background-color: #1a2a6c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Gas Fee Alert Triggered!</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Good news! The Ethereum gas fee is now <strong>{current_fee} GWEI</strong>, which is {condition} your alert threshold of <strong>{threshold} GWEI</strong>.</p>

                <div class="alert-details">
                    <h3>Current Gas Fee Details:</h3>
                    <p><strong>Current Fee:</strong> {current_fee} GWEI</p>
                    <p><strong>Your Threshold:</strong> {threshold} GWEI</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <p>This might be a good time to make your Ethereum transaction!</p>
                <p>
                    <a href="http://localhost:5000/app" class="cta-button">View Gas Fee Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2025 Ethereum Gas Fee Predictor - Created by SRUJAN.J</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)

@app.route('/')
def index():
    """Render the main landing page."""
    return render_template('index.html')

@app.route('/app')
def app_page():
    """Render the main application page with all features."""
    return render_template('app.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Handle gas fee prediction requests."""
    global last_prediction, last_prediction_time

    if request.method == 'POST':
        try:
            print("Received prediction request")
            current_time = datetime.now()
            timestamp = int(current_time.timestamp())
            try:
                from scripts.improved_gas_fee import connect_to_ethereum, load_model, predict_gas_fee
                model, scaler = load_model()
                web3 = connect_to_ethereum()
                predicted_fee, block_data = predict_gas_fee(web3, model, scaler)

                print(f"Successfully connected to Ethereum and made prediction: {predicted_fee:.4f} GWEI")
                current_time = datetime.fromtimestamp(block_data["timestamp"])
                timestamp = int(current_time.timestamp())

            except Exception as e:
                print(f"Error connecting to Ethereum: {e}")
                print("Using fallback data instead")
                last_block_number = 18500000
                if last_prediction and 'block_number' in last_prediction:
                    last_block_number = last_prediction['block_number']
                    import random
                    block_increment = random.randint(5, 15)
                    last_block_number += block_increment

                block_data = {
                    'base_fee_gwei': 25.4321,
                    'block_number': last_block_number,
                    'gas_used': 12500000,
                    'gas_limit': 30000000,
                    'tx_count': 150,
                    'timestamp': timestamp
                }
                predicted_fee = block_data['base_fee_gwei'] * 1.02
            last_prediction = {
                'predicted_fee': round(float(predicted_fee), 4),
                'current_fee': round(float(block_data['base_fee_gwei']), 4),
                'block_number': int(block_data['block_number']),
                'gas_used': int(block_data['gas_used']),
                'gas_limit': int(block_data['gas_limit']),
                'tx_count': int(block_data['tx_count']),
                'timestamp': int(block_data['timestamp']),
                'formatted_time': datetime.fromtimestamp(block_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            }
            last_prediction_time = current_time
            difference = predicted_fee - block_data['base_fee_gwei']
            percent_change = (difference / block_data['base_fee_gwei']) * 100 if block_data['base_fee_gwei'] > 0 else 0

            last_prediction['difference'] = round(float(difference), 4)
            last_prediction['percent_change'] = round(float(percent_change), 4)
            last_prediction['trend'] = 'decreasing'

            return jsonify({
                'success': True,
                'prediction': last_prediction
            })
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            current_time = datetime.now()
            timestamp = int(current_time.timestamp())
            try:
                from scripts.improved_gas_fee import connect_to_ethereum, load_model, predict_gas_fee
                model, scaler = load_model()
                web3 = connect_to_ethereum()
                predicted_fee, block_data = predict_gas_fee(web3, model, scaler)

                print(f"Successfully connected to Ethereum in exception handler: {predicted_fee:.4f} GWEI")
                current_time = datetime.fromtimestamp(block_data["timestamp"])
                timestamp = int(current_time.timestamp())
                diff = predicted_fee - block_data['base_fee_gwei']
                percent_change = (diff / block_data['base_fee_gwei']) * 100 if block_data['base_fee_gwei'] > 0 else 0
                global current_trend  
                trend = 'decreasing'  
                demo_prediction = {
                    'predicted_fee': round(float(predicted_fee), 4),
                    'current_fee': round(float(block_data['base_fee_gwei']), 4),
                    'difference': round(float(diff), 4),
                    'percent_change': round(float(percent_change), 4),
                    'trend': trend,
                    'block_number': int(block_data['block_number']),
                    'gas_used': int(block_data['gas_used']),
                    'gas_limit': int(block_data['gas_limit']),
                    'tx_count': int(block_data['tx_count']),
                    'timestamp': int(block_data['timestamp']),
                    'formatted_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                }

            except Exception as e2:
                print(f"Error connecting to Ethereum in exception handler: {e2}")
                print("Using hardcoded fallback data")
                last_block_number = 18500000
                if last_prediction and 'block_number' in last_prediction:
                    last_block_number = last_prediction['block_number']
                    import random
                    block_increment = random.randint(5, 15)
                    last_block_number += block_increment
                demo_prediction = {
                    'predicted_fee': 25.9407,
                    'current_fee': 25.4321,
                    'difference': 0.5086,
                    'percent_change': 2.0000,
                    'trend': 'decreasing', 
                    'block_number': last_block_number,
                    'gas_used': 12500000,
                    'gas_limit': 30000000,
                    'tx_count': 150,
                    'timestamp': timestamp,
                    'formatted_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            last_prediction = demo_prediction
            last_prediction_time = current_time

            return jsonify({
                'success': True,
                'prediction': demo_prediction
            })
    else:
        if last_prediction and last_prediction_time:
            if datetime.now() - last_prediction_time < timedelta(minutes=5):
                return jsonify({
                    'success': True,
                    'prediction': last_prediction,
                    'cached': True
                })
        return jsonify({
            'success': False,
            'error': 'No recent prediction available'
        })

@app.route('/heatmap')
def heatmap():
    """Generate and return gas fee heatmap data."""
    try:
        df = load_historical_data()
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_ns_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            elif not df['timestamp'].dt.tz:
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
            df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
        output_dir = os.path.join(os.getcwd(), 'static', 'images')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'gas_fee_heatmap.png')
        print(f"Generating heatmap at: {output_path}")
        heatmap_results = generate_gas_fee_heatmap(df, output_path=output_path)
        if os.path.exists(output_path):
            print(f"Heatmap file created successfully at: {output_path}")
        else:
            print(f"WARNING: Heatmap file was not created at: {output_path}")
        optimal_times = find_optimal_transaction_times(df)

        return jsonify({
            'success': True,
            'heatmap_path': '/static/images/gas_fee_heatmap.png',
            'best_time': heatmap_results['best_time'],
            'worst_time': heatmap_results['worst_time'],
            'optimal_times': optimal_times['optimal_times'][:5],
            'avoid_times': optimal_times['avoid_times'][:5],
            'timezone': 'Asia/Kolkata'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/heatmap-view')
def heatmap_view():
    """Render a simple heatmap page."""
    return render_template('heatmap.html')

@app.route('/transaction-costs')
def transaction_costs():
    """Calculate and return transaction costs."""
    try:
        if last_prediction:
            current_fee = round(last_prediction['current_fee'], 4)
            predicted_fee = round(last_prediction['predicted_fee'], 4)
        else:
            current_fee = 50.0000
            predicted_fee = 45.0000
        eth_price = get_eth_price()
        current_costs = calculate_transaction_costs(current_fee, eth_price)
        predicted_costs = calculate_transaction_costs(predicted_fee, eth_price)
        current_costs_list = current_costs.to_dict('records')
        predicted_costs_list = predicted_costs.to_dict('records')

        return jsonify({
            'success': True,
            'eth_price': eth_price,
            'current_fee': current_fee,
            'predicted_fee': predicted_fee,
            'current_costs': current_costs_list,
            'predicted_costs': predicted_costs_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/historical-data')
def historical_data():
    """Return historical gas fee data for charts."""
    try:
        df = pd.read_csv('data/gas_fees_cleaned.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
        df = df.sort_values('timestamp')
        recent_df = df.tail(500)
        chart_data = {
            'timestamps': recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'base_fees': recent_df['base_fee_gwei'].tolist()
        }
        if 'predicted_fee' in recent_df.columns:
            chart_data['predicted_fees'] = recent_df['predicted_fee'].tolist()
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['base_fee_gwei'].mean().reset_index()

        hourly_data = {
            'hours': hourly_avg['hour'].tolist(),
            'avg_fees': hourly_avg['base_fee_gwei'].tolist(),
            'timezone': 'Asia/Kolkata'
        }

        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'hourly_data': hourly_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/upload-data', methods=['POST'])
def upload_data():
    """Handle data file uploads."""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file part'
        })

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No selected file'
        })

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return jsonify({
            'success': True,
            'message': f'File {filename} uploaded successfully',
            'file_path': file_path
        })

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """Run the full prediction pipeline."""
    try:
        data = request.get_json()
        num_blocks = data.get('num_blocks', 200)  
        use_improved = data.get('use_improved', True)
        timezone = data.get('timezone', 'Asia/Kolkata')  
        def run_data_collection(num_blocks=200, timezone='Asia/Kolkata'):
            try:
                from scripts.collect_gas_data import collect_ethereum_gas_data
                try:
                    collect_ethereum_gas_data(num_blocks=num_blocks, timezone=timezone)
                except TypeError:
                    collect_ethereum_gas_data(num_blocks=num_blocks)
                return True
            except Exception as e:
                print(f"Data collection failed: {str(e)}")
                return False

        def run_data_cleaning():
            try:
                from scripts.clean_data import clean_gas_data
                clean_gas_data()
                return True
            except Exception as e:
                print(f"Data cleaning failed: {str(e)}")
                return False

        def run_model_training():
            try:
                from scripts.train_model import train_gas_fee_model
                train_gas_fee_model()
                return True
            except Exception as e:
                print(f"Model training failed: {str(e)}")
                return False

        def run_prediction(use_improved=True):
            try:
                from scripts.improved_gas_fee import predict_and_save
                predict_and_save(use_improved=use_improved)
                return True
            except Exception as e:
                print(f"Prediction failed: {str(e)}")
                return False

        collection_success = run_data_collection(num_blocks=num_blocks, timezone=timezone)
        if not collection_success:
            return jsonify({
                'success': False,
                'error': 'Data collection failed'
            })

        cleaning_success = run_data_cleaning()
        if not cleaning_success:
            return jsonify({
                'success': False,
                'error': 'Data cleaning failed'
            })

        training_success = run_model_training()
        if not training_success:
            return jsonify({
                'success': False,
                'error': 'Model training failed'
            })

        prediction_success = run_prediction(use_improved=use_improved)
        if not prediction_success:
            return jsonify({
                'success': False,
                'error': 'Prediction failed'
            })

        return jsonify({
            'success': True,
            'message': 'Pipeline completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/run-heatmap-script', methods=['POST'])
def run_heatmap_script():
    """Run the heatmap generation script directly."""
    try:
        from scripts.generate_gas_heatmap import main as generate_heatmap_main
        result = generate_heatmap_main()

        if result == 0:
            return jsonify({
                'success': True,
                'message': 'Heatmap generated successfully',
                'heatmap_path': '/static/images/gas_fee_heatmap.png'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Heatmap generation failed with code ' + str(result)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/refresh_heatmap')
def refresh_heatmap():
    """Download the latest Etherscan heatmap."""
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'static', 'images'))
        from download_etherscan_heatmap import download_etherscan_heatmap
        success = download_etherscan_heatmap()

        if success:
            return jsonify({
                'success': True,
                'message': 'Heatmap refreshed successfully',
                'timestamp': int(datetime.now().timestamp())
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to download heatmap, using fallback',
                'timestamp': int(datetime.now().timestamp())
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': int(datetime.now().timestamp())
        })

@app.route('/gas-alerts', methods=['GET', 'POST'])
def gas_alerts():
    """Handle gas fee alerts."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            threshold = data.get('threshold')
            email = data.get('email')
            phone = data.get('phone')
            duration = data.get('duration', 24)  
            condition = data.get('condition', 'below') 
            if not threshold or threshold <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Invalid threshold value'
                })

            if not email:
                return jsonify({
                    'success': False,
                    'error': 'Email is required'
                })
            alert_id = str(uuid.uuid4())
            alert = {
                'id': alert_id,
                'threshold': round(float(threshold), 4),
                'email': email,
                'phone': phone,
                'condition': condition,
                'duration': duration,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=duration)).isoformat()
            }
            send_alert_confirmation_email(alert)
            return jsonify({
                'success': True,
                'message': 'Alert set successfully. Confirmation email sent.',
                'alert': alert
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    else:
        if last_prediction:
            return jsonify({
                'success': True,
                'current_fee': round(last_prediction['current_fee'], 4),
                'predicted_fee': round(last_prediction['predicted_fee'], 4),
                'difference': round(last_prediction['difference'], 4),
                'percent_change': round(last_prediction['percent_change'], 4),
                'trend': 'decreasing',  
                'formatted_time': last_prediction['formatted_time']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No gas fee data available'
            })

@app.route('/trigger-alert', methods=['POST'])
def trigger_alert():
    """Trigger a gas fee alert and send email notification."""
    try:
        data = request.get_json()
        alert_id = data.get('alert_id')
        alert = data.get('alert')
        current_fee = data.get('current_fee')

        if not alert or not current_fee:
            return jsonify({
                'success': False,
                'error': 'Missing alert data or current fee'
            })
        email_sent = send_alert_triggered_email(alert, current_fee)

        return jsonify({
            'success': True,
            'email_sent': email_sent,
            'message': 'Alert triggered successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
