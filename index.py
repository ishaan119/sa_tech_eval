from flask import Flask, jsonify, render_template_string, request
import redis
import time
from datetime import datetime

app = Flask(__name__)

# Redis Configuration
REDIS_OSS_HOST = '34.47.152.199'  
REDIS_OSS_PORT = 13379  
REDIS_ENTERPRISE_HOST = '35.200.211.116' 
REDIS_ENTERPRISE_PORT = 14187

# Redis Connections
try:
    redis_oss = redis.Redis(host=REDIS_OSS_HOST, port=REDIS_OSS_PORT, decode_responses=True)
    redis_enterprise = redis.Redis(host=REDIS_ENTERPRISE_HOST, port=REDIS_ENTERPRISE_PORT, decode_responses=True)
except Exception as e:
    print(f"Redis connection error: {e}")

# HTML Template for simple UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Redis Replication Demo</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: #f7f7f7; }
        .header { background-color: #ca212a; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; }
        .header p { margin: 5px 0 0; }
        .main-container { display: flex; justify-content: space-around; padding: 20px; gap: 20px; }
        .panel { background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex-basis: 48%; }
        .panel-header { background-color: #f2f2f2; padding: 15px; border-bottom: 1px solid #ddd; border-radius: 8px 8px 0 0; }
        .panel-header h2 { margin: 0; font-size: 1.2em; }
        .panel-header p { margin: 5px 0 0; font-size: 0.9em; color: #666; }
        .panel-body { padding: 20px; }
        .button { 
            background-color: #ca212a; color: white; padding: 12px 20px; 
            border: none; cursor: pointer; margin: 10px 0; border-radius: 5px; font-size: 1em;
            display: block; width: 100%;
        }
        .button:hover { background-color: #a91b23; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .input-group input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: calc(50% - 22px); }
        .result-box { 
            background-color: #2d2d2d; color: #f1f1f1; padding: 15px; margin-top: 20px; 
            border-radius: 5px; white-space: pre-wrap; font-family: "SF Mono", "Fira Code", "Consolas", monospace;
            font-size: 0.9em; max-height: 400px; overflow-y: auto;
        }
        .result-box.error { border-left: 5px solid #d9534f; }
        .result-box.success { border-left: 5px solid #5cb85c; }
        .result-title { font-weight: bold; margin-bottom: 10px; }
        .result-item { margin-bottom: 5px; }
        .result-item strong { color: #a5d6ff; }
        .footer { text-align: center; padding: 20px; font-size: 0.9em; color: #888; }
        .utils { display: flex; gap: 10px; }
        .utils .button { background-color: #6c757d; }
        .utils .button:hover { background-color: #5a6268; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Redis OSS to Redis Enterprise Replication</h1>
        <p>A demonstration of the "Replica Of" feature.</p>
    </div>

    <div class="main-container">
        <!-- Redis OSS Panel -->
        <div class="panel">
            <div class="panel-header">
                <h2>1. Source: Redis OSS</h2>
                <p>Insert a range of numbers into the source database.</p>
            </div>
            <div class="panel-body">
                <div class="input-group">
                    <label for="startValue">Value Range:</label>
                    <input type="number" id="startValue" value="1" min="1">
                    <input type="number" id="endValue" value="100" min="1">
                </div>
                <button class="button" onclick="insertData()">Insert Values</button>
                <div id="insert-result" class="result-box" style="display:none;"></div>
            </div>
        </div>

        <!-- Redis Enterprise Panel -->
        <div class="panel">
            <div class="panel-header">
                <h2>2. Target: Redis Enterprise</h2>
                <p>Extract the replicated data from the target database.</p>
            </div>
            <div class="panel-body">
                <button class="button" onclick="extractData()">Extract in Reverse Order</button>
                <div id="extract-result" class="result-box" style="display:none;"></div>
            </div>
        </div>
    </div>
    
    <div class="main-container" style="padding-top: 0;">
        <div class="panel">
            <div class="panel-header">
                <h2>Utilities</h2>
            </div>
            <div class="panel-body utils">
                <button class="button" onclick="checkConnections()">Check Connections</button>
                <button class="button" onclick="clearData()">Clear Data</button>
            </div>
            <div id="util-result" class="result-box" style="display:none; margin: 20px;"></div>
        </div>
    </div>

    <div class="footer">
        <p>This application demonstrates inserting data into a Redis OSS instance, which is then replicated to a Redis Enterprise database.</p>
    </div>

    <script>
        async function handleRequest(url, options, resultElementId) {
            const resultBox = document.getElementById(resultElementId);
            resultBox.style.display = 'block';
            resultBox.className = 'result-box';
            resultBox.innerHTML = 'Loading...';

            try {
                const response = await fetch(url, options);
                const data = await response.json();
                renderResult(resultBox, data);
            } catch (error) {
                const errorData = { status: 'error', message: 'Network or client-side error.', data: { details: error.message } };
                renderResult(resultBox, errorData);
            }
        }

        function insertData() {
            const start = document.getElementById('startValue').value;
            const end = document.getElementById('endValue').value;
            handleRequest('/insert-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start: parseInt(start), end: parseInt(end) })
            }, 'insert-result');
        }

        function extractData() {
            handleRequest('/extract-data', {}, 'extract-result');
        }

        function checkConnections() {
            handleRequest('/check-connections', {}, 'util-result');
        }

        function clearData() {
            handleRequest('/clear-data', {}, 'util-result');
        }

        function renderResult(element, response) {
            element.innerHTML = '';
            element.classList.add(response.status === 'success' ? 'success' : 'error');

            const title = document.createElement('div');
            title.className = 'result-title';
            title.textContent = `${response.status.toUpperCase()}: ${response.message}`;
            element.appendChild(title);

            if (response.data) {
                for (const [key, value] of Object.entries(response.data)) {
                    const item = document.createElement('div');
                    item.className = 'result-item';
                    let content = `<strong>${key}:</strong> `;
                    if (typeof value === 'object' && value !== null) {
                        content += JSON.stringify(value, null, 2);
                    } else {
                        content += value;
                    }
                    item.innerHTML = content;
                    element.appendChild(item);
                }
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/insert-data', methods=['POST'])
def insert_data():
    """Insert user-specified range of values into Redis OSS using a LIST data type"""
    try:
        data = request.get_json()
        start_value = data.get('start', 1)
        end_value = data.get('end', 100)

        if not all(isinstance(v, int) for v in [start_value, end_value]):
            return jsonify({
                'status': 'error',
                'message': 'Invalid input: Start and end values must be integers.'
            }), 400
        if start_value >= end_value:
            return jsonify({
                'status': 'error',
                'message': 'Invalid range: Start value must be less than end value.'
            }), 400
        if end_value - start_value > 10000:
            return jsonify({
                'status': 'error',
                'message': 'Range too large: Maximum 10,000 values allowed.'
            }), 400

        start_time = time.time()
        pipeline = redis_oss.pipeline()
        pipeline.delete('numbers_list')
        for i in range(start_value, end_value + 1):
            pipeline.rpush('numbers_list', i)
        pipeline.execute()
        
        list_length = redis_oss.llen('numbers_list')
        end_time = time.time()

        return jsonify({
            'status': 'success',
            'message': f'Successfully inserted {list_length} values into Redis OSS.',
            'data': {
                'redis_key': 'numbers_list',
                'range': f'{start_value} to {end_value}',
                'total_items_inserted': list_length,
                'execution_time_seconds': f"{end_time - start_time:.4f}",
                'target_server': f"{REDIS_OSS_HOST}:{REDIS_OSS_PORT}",
                'timestamp_utc': datetime.utcnow().isoformat()
            }
        })

    except redis.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': f'Connection failed to Redis OSS at {REDIS_OSS_HOST}:{REDIS_OSS_PORT}.'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred during data insertion.',
            'data': {'error_details': str(e)}
        }), 500

@app.route('/extract-data')
def extract_data():
    """Extract values in reverse order from Redis Enterprise DB"""
    try:
        start_time = time.time()
        
        if not redis_enterprise.exists('numbers_list'):
            return jsonify({
                'status': 'error',
                'message': 'Data not found in Redis Enterprise.',
                'data': {
                    'details': 'The key "numbers_list" does not exist. Replication may not be complete or configured correctly.'
                }
            }), 404
        
        # Retrieve the list from Redis.
        # The values were inserted with RPUSH, so they are in insertion order (e.g., 1, 2, 3...).
        values = redis_enterprise.lrange('numbers_list', 0, -1)
        values_as_int = [int(v) for v in values]
        
        # Reverse the list to fulfill the "extract in reverse order" requirement.
        values_as_int.reverse()
        
        end_time = time.time()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully extracted {len(values_as_int)} values from Redis Enterprise in reverse order.',
            'data': {
                'redis_key': 'numbers_list',
                'total_items_extracted': len(values_as_int),
                'values': values_as_int,
                'note': 'Values were retrieved from Redis Enterprise and then reversed in the application.',
                'execution_time_seconds': f"{end_time - start_time:.4f}",
                'source_server': f"{REDIS_ENTERPRISE_HOST}:{REDIS_ENTERPRISE_PORT}",
                'timestamp_utc': datetime.utcnow().isoformat()
            }
        })
        
    except redis.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': f'Connection failed to Redis Enterprise at {REDIS_ENTERPRISE_HOST}:{REDIS_ENTERPRISE_PORT}.'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred during data extraction.',
            'data': {'error_details': str(e)}
        }), 500

@app.route('/check-connections')
def check_connections():
    """Check connectivity to both Redis instances"""
    oss_status = {'status': 'error', 'details': {}}
    enterprise_status = {'status': 'error', 'details': {}}

    try:
        redis_oss.ping()
        info = redis_oss.info('server')
        replication_info = redis_oss.info('replication')
        oss_status = {
            'status': 'connected',
            'details': {
                'host': REDIS_OSS_HOST,
                'port': REDIS_OSS_PORT,
                'version': info.get('redis_version'),
                'role': replication_info.get('role')
            }
        }
    except Exception as e:
        oss_status['details']['error'] = str(e)

    try:
        redis_enterprise.ping()
        info = redis_enterprise.info('server')
        replication_info = redis_enterprise.info('replication')
        enterprise_status = {
            'status': 'connected',
            'details': {
                'host': REDIS_ENTERPRISE_HOST,
                'port': REDIS_ENTERPRISE_PORT,
                'version': info.get('redis_version'),
                'role': replication_info.get('role')
            }
        }
    except Exception as e:
        enterprise_status['details']['error'] = str(e)

    all_connected = oss_status['status'] == 'connected' and enterprise_status['status'] == 'connected'

    return jsonify({
        'status': 'success' if all_connected else 'error',
        'message': 'Redis connection status check complete.',
        'data': {
            'redis_oss': oss_status,
            'redis_enterprise': enterprise_status
        }
    })

@app.route('/clear-data')
def clear_data():
    """Clear data from both Redis instances for a clean test"""
    oss_result = {}
    enterprise_result = {}

    try:
        deleted_oss = redis_oss.delete('numbers_list')
        oss_result = {
            'status': 'success',
            'message': f'Cleared {deleted_oss} key(s) from Redis OSS.'
        }
    except Exception as e:
        oss_result = {'status': 'error', 'message': str(e)}

    try:
        # This is mostly for cleanup; replication should handle the delete
        deleted_enterprise = redis_enterprise.delete('numbers_list')
        enterprise_result = {
            'status': 'success',
            'message': f'Cleared {deleted_enterprise} key(s) from Redis Enterprise.'
        }
    except Exception as e:
        enterprise_result = {'status': 'error', 'message': str(e)}

    return jsonify({
        'status': 'success',
        'message': 'Clear data operation finished.',
        'data': {
            'redis_oss_cleanup': oss_result,
            'redis_enterprise_cleanup': enterprise_result
        }
    })

if __name__ == '__main__':
    print("Starting Redis Flask Application...")
    print(f"Redis OSS: {REDIS_OSS_HOST}:{REDIS_OSS_PORT}")
    print(f"Redis Enterprise: {REDIS_ENTERPRISE_HOST}:{REDIS_ENTERPRISE_PORT}")
    
    app.run(debug=True, host='0.0.0.0', port=9000)