import os
from flask import Flask, request
from psycopg_pool import ConnectionPool

def dbConnect():
    """Create a connection pool to connect to Postgres"""
    db_host = os.getenv('DB_HOST')
    db_database = os.getenv('DB_DATABASE')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    # Create a connection string/URL for the database
    db_url = f'host = {db_host} dbname = {db_database} user = {
        db_user} password = {db_password}'
    # db_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_database}"

    # Connect to Postgres database
    conn_pool = ConnectionPool(db_url)
    conn_pool.wait()

    return conn_pool

# Create a connection pool to Postgres
pool = dbConnect()

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
    
def save_item(priority, task, table, pool):
    """Save an item/task to the database"""

    # Connect to an existing Database
    with pool.connection() as conn:

        # Open a cursor to operate database connectiom
        with conn.cursor() as cur:

            # prepare the database query
            query = f"INSERT INTO {table} (priority, task) VALUES (%s, %s)"

            # send the query to PostgreSQL with the actual values 
            cur.execute(query, (priority, task))

            # Make the changes to the database persistent
            conn.commit()

def get_items(table, pool):
    """Get all items/tasks from the database"""

    # Connect to an existing Database
    with pool.connection() as conn:

        # Open a cursor to operate database connectiom
        with conn.cursor() as cur:

            # prepare the database query
            query = f"SELECT item_id, priority, task  FROM {table}"

            # send the query to Postgres
            cur.execute(query)

            items = []

            for rec in cur:
                item = {
                    'item_id': rec[0],
                    'priority': rec[1],
                    'task': rec[2]
                }
                items.append(item)

            # return a list of items
            # results = cur.fetchall()
            return items
        
@app.route('/items', methods=['GET', 'POST'])
def items():
    match request.method:
        case 'GET':
            items = get_items('item', pool)

            return items, 200
        case 'POST':
            req = request.get_json()
            save_item(req['priority'], req['task'], 'item', pool)

            return {'Message': 'Item Saved!'}, 201
        case _:
            return {'Message': 'Invalid request'}, 405
