from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import time
import threading
from twilio.rest import Client
from dotenv import load_dotenv
from flask_cors import CORS


app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Store active price monitors
active_monitors = {}

class PriceMonitor:
    def __init__(self, crypto_id, target_price, check_above, interval, twilio_config):
        self.crypto_id = crypto_id
        self.target_price = target_price
        self.check_above = check_above
        self.interval = interval
        self.twilio_config = twilio_config
        self.running = True
        self.thread = threading.Thread(target=self.monitor_price)
        self.last_price = None
        self.last_updated = None
    
    def start(self):
        self.thread.start()
        return self.thread.ident
    
    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2)
    
    def get_crypto_price(self):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={self.crypto_id}&vs_currencies=usd"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if self.crypto_id in data:
                    self.last_price = data[self.crypto_id]['usd']
                    self.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
                    return self.last_price
            return None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def check_price(self, current_price):
        if self.check_above:
            return current_price >= self.target_price
        else:
            return current_price <= self.target_price
    
    def make_twilio_call(self):
        try:
            account_sid = self.twilio_config['account_sid']
            auth_token = self.twilio_config['auth_token']
            studio_flow_sid = self.twilio_config['studio_flow_sid']
            call_from = self.twilio_config['call_from']
            call_to = self.twilio_config['call_to']
            
            client = Client(account_sid, auth_token)
            execution = client.studio.v2.flows(
                studio_flow_sid
            ).executions.create(to=call_to, from_=call_from)
            
            print(f"Called {execution.sid}")
            return True
        except Exception as e:
            print(f"Error making Twilio call: {e}")
            return False
    
    def monitor_price(self):
        while self.running:
            current_price = self.get_crypto_price()
            if current_price is not None:
                print(f"Current {self.crypto_id} price: ${current_price}")
                
                if self.check_price(current_price):
                    print(f"Target price {'above' if self.check_above else 'below'} ${self.target_price} reached!")
                    self.make_twilio_call()
                    self.running = False
                    break
                else:
                    print(f"Target price not reached. Waiting...")
            
            time.sleep(self.interval)

@app.route('/api/start-monitor', methods=['POST'])
def start_monitor():
    data = request.json
    
    # Validate required fields
    required_fields = ['cryptoId', 'targetPrice', 'checkAbove', 'interval', 'callTo']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Load Twilio config from .env
    load_dotenv()
    twilio_config = {
        'account_sid': os.environ['ACCOUNT_SID'],
        'auth_token': os.environ['AUTH_TOKEN'],
        'studio_flow_sid': os.environ['STUDIO_FLOW_SID'],
        'call_from': os.environ['TWILIO_PHONE_NUMBER'],
        'call_to': data['callTo']
    }
    
    # Create and start price monitor
    monitor = PriceMonitor(
        crypto_id=data['cryptoId'],
        target_price=float(data['targetPrice']),
        check_above=data['checkAbove'],
        interval=int(data['interval']),
        twilio_config=twilio_config
    )
    
    # Start the monitor and get its ID
    monitor_id = monitor.start()
    active_monitors[monitor_id] = monitor
    
    return jsonify({
        'status': 'success',
        'message': 'Price monitor started',
        'monitorId': monitor_id
    })

@app.route('/api/stop-monitor/<int:monitor_id>', methods=['POST'])
def stop_monitor(monitor_id):
    if monitor_id in active_monitors:
        active_monitors[monitor_id].stop()
        del active_monitors[monitor_id]
        return jsonify({
            'status': 'success',
            'message': 'Price monitor stopped'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Monitor not found'
        }), 404

@app.route('/api/status/<int:monitor_id>', methods=['GET'])
def get_status(monitor_id):
    if monitor_id in active_monitors:
        monitor = active_monitors[monitor_id]
        return jsonify({
            'status': 'running' if monitor.running else 'stopped',
            'lastPrice': monitor.last_price,
            'lastUpdated': monitor.last_updated,
            'cryptoId': monitor.crypto_id,
            'targetPrice': monitor.target_price,
            'checkAbove': monitor.check_above
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Monitor not found'
        }), 404

@app.route('/api/make-test-call', methods=['POST'])
def make_test_call():
    data = request.json
    
    # Validate required fields
    if 'callTo' not in data:
        return jsonify({'error': 'Missing required field: callTo'}), 400
    
    try:
        # Load Twilio config from .env
        load_dotenv()
        account_sid = os.environ['ACCOUNT_SID']
        auth_token = os.environ['AUTH_TOKEN']
        studio_flow_sid = os.environ['STUDIO_FLOW_SID']
        call_from = os.environ['TWILIO_PHONE_NUMBER']
        call_to = data['callTo']
        
        client = Client(account_sid, auth_token)
        execution = client.studio.v2.flows(
            studio_flow_sid
        ).executions.create(to=call_to, from_=call_from)
        
        return jsonify({
            'status': 'success',
            'message': 'Test call made successfully',
            'executionSid': execution.sid
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Serve static files for frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path == "":
        # Return index.html
        return send_from_directory(app.static_folder, 'index.html')
    else:
        # Try to serve the static file
        try:
            return send_from_directory(app.static_folder, path)
        except:
            # If not found, return index.html (for SPA)
            return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)