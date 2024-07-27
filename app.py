import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Welcome to my Flask Test App!"

@app.route('/about', methods=['GET'])
def about():
    version = os.getenv('APP_VERSION', 'unknown')
    return {'app_version': version}, 200

@app.route('/secret', methods=['GET'])
def secret():
    credentials = dict()

    credentials['db_password'] = os.getenv('DB_PASSWORD', 'null')
    credentials['app_token'] = os.getenv('APP_TOKEN', 'null')
    credentials['api_secret']= open('/run/secrets/api_key', 'r').read().strip('\n')

    return credentials, 200

@app.route('/config', methods=['GET'])
def config():
    config = dict()

    config['config_dev'] = open('/config-dev.yaml', 'r').read()
    config['config_dev-v2'] = open('/config-dev-v2.yaml', 'r').read()

    return config, 200

@app.route('/volumes', methods=['GET', 'POST'])
def volume():
    filename = '/data/data.txt'

    if request.method == 'POST':
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # volume = request.get_data().decode('utf-8')
        with open(filename, 'w') as file:
            file.write('Customer Record')
        
        return 'Saved!', 200
    else:
        try:
            with open(filename, 'r') as file:
                volume = file.read()
        except FileNotFoundError:
            volume = 'No data'

        return volume, 200
