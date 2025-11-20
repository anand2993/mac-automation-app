import os
import paramiko
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from prometheus_client import Counter, generate_latest, Gauge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_change_me')

# Prometheus Metrics
REQUEST_COUNT = Counter('app_request_count', 'Total app requests', ['method', 'endpoint'])
APP_OPEN_COUNT = Counter('app_open_count', 'Number of times an app switch was toggled', ['app_name'])
SYSTEM_STATUS = Gauge('system_status', 'System status (1=Up, 0=Down)')

# Mock Database for Login
USERS = {
    "admin": "password123"  # In production, use hashed passwords!
}

def execute_ssh_command(command):
    """Executes a command on the host machine via SSH."""
    host = os.environ.get('HOST_IP', 'host.docker.internal')
    port = int(os.environ.get('HOST_SSH_PORT', 22))
    username = os.environ.get('HOST_USER')
    password = os.environ.get('HOST_PASSWORD')

    if not username or not password:
        logger.error("SSH credentials not configured")
        return False, "SSH Credentials not configured."

    try:
        logger.info(f"Executing SSH command: {command}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password, timeout=5)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        client.close()
        if error:
            logger.error(f"SSH command failed: {error}")
            return False, error
        logger.info(f"SSH command succeeded: {output}")
        return True, output
    except Exception as e:
        logger.error(f"SSH connection error: {str(e)}")
        return False, str(e)

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/', methods=['GET', 'POST'])
def login():
    REQUEST_COUNT.labels('GET', '/').inc()
    if request.method == 'POST':
        REQUEST_COUNT.labels('POST', '/').inc()
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['user'] = username
            logger.info(f"User '{username}' logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for user '{username}'")
            return render_template('index.html', error="Invalid credentials")
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    REQUEST_COUNT.labels('GET', '/dashboard').inc()
    SYSTEM_STATUS.set(1)
    return render_template('dashboard.html', user=session['user'])

@app.route('/open-app', methods=['POST'])
def open_app():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    app_name = data.get('app_name')
    
    logger.info(f"User '{session['user']}' requested to open app: {app_name}")
    APP_OPEN_COUNT.labels(app_name).inc()
    
    # Mapping friendly names to actual Mac app names or commands
    app_map = {
        'facetime': 'FaceTime',
        'whatsapp': 'WhatsApp',
        'docker': 'Docker',
        'terminal': 'Terminal'
    }
    
    target_app = app_map.get(app_name.lower())
    if not target_app:
        logger.warning(f"Unknown application requested: {app_name}")
        return jsonify({'success': False, 'message': 'Unknown application'}), 400

    # Command to open app on Mac
    cmd = f'open -a "{target_app}"'
    
    success, msg = execute_ssh_command(cmd)
    
    if success:
        logger.info(f"Successfully opened {target_app}")
        return jsonify({'success': True, 'message': f'Opened {target_app}'})
    else:
        logger.error(f"Failed to open {target_app}: {msg}")
        return jsonify({'success': False, 'message': f'Failed: {msg}'})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
