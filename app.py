from flask import Flask, request, render_template, redirect, url_for, session, flash
import datetime
import sqlite3
import os
import re
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Admin credentials for testing
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'  # Plain text password for testing

# Database setup
def init_db():
    conn = sqlite3.connect('iplogs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        ip TEXT NOT NULL,
        ipv6 TEXT,
        user_agent TEXT NOT NULL,
        os_type TEXT NOT NULL,
        os_version TEXT NOT NULL,
        browser TEXT NOT NULL,
        referrer TEXT,
        timestamp DATETIME NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

def parse_user_agent(ua):
    os_type = os_version = browser = "Unknown"
    if not ua:
        return os_type, os_version, browser
        
    # OS Detection
    if re.search(r'Windows NT 10', ua):
        os_type = "Windows"
        os_version = "10"
    elif re.search(r'Windows NT 6.3', ua):
        os_type = "Windows"
        os_version = "8.1"
    elif re.search(r'Windows NT 6.2', ua):
        os_type = "Windows"
        os_version = "8"
    elif re.search(r'Windows NT 6.1', ua):
        os_type = "Windows"
        os_version = "7"
    elif re.search(r'Mac OS X ([0-9_]+)', ua):
        os_type = "macOS"
        os_version = re.search(r'Mac OS X ([0-9_]+)', ua).group(1).replace('_', '.')
    elif re.search(r'Linux', ua):
        os_type = "Linux"
        os_version = re.search(r'Linux ([a-zA-Z0-9]+)', ua).group(1) if re.search(r'Linux ([a-zA-Z0-9]+)', ua) else "Unknown"
    elif re.search(r'Android ([0-9.]+)', ua):
        os_type = "Android"
        os_version = re.search(r'Android ([0-9.]+)', ua).group(1)
    elif re.search(r'iPhone|iPad', ua):
        os_type = "iOS"
        os_version = re.search(r'OS ([0-9_]+)', ua).group(1).replace('_', '.') if re.search(r'OS ([0-9_]+)', ua) else "Unknown"
    
    # Browser Detection
    if re.search(r'Chrome/([0-9.]+)', ua):
        browser = "Chrome"
    elif re.search(r'Firefox/([0-9.]+)', ua):
        browser = "Firefox"
    elif re.search(r'Safari/', ua) and not re.search(r'Chrome/', ua):
        browser = "Safari"
    elif re.search(r'Edge/([0-9.]+)', ua):
        browser = "Edge"
    elif re.search(r'OPR/([0-9.]+)', ua):
        browser = "Opera"
    elif re.search(r'Trident/.*rv:([0-9.]+)', ua):
        browser = "Internet Explorer"
    
    return os_type, os_version, browser

def get_client_ip():
    """Get client IP with proxy support"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    return request.remote_addr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def user_form():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            
            # Input validation
            if not name:
                flash("Name is required", "danger")
                return render_template('user_form.html')
            
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                flash("Invalid email address", "danger")
                return render_template('user_form.html')
                
            if phone and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
                flash("Invalid phone number format", "danger")
                return render_template('user_form.html')
            
            # Get client information
            ip = get_client_ip()
            ipv6 = request.remote_addr if ':' in request.remote_addr else ''
            user_agent = request.headers.get('User-Agent', '')
            referrer = request.headers.get('Referer', '')
            timestamp = datetime.datetime.now()
            os_type, os_version, browser = parse_user_agent(user_agent)
            
            # Save to database
            conn = sqlite3.connect('iplogs.db')
            c = conn.cursor()
            c.execute('''INSERT INTO logs (
                name, email, phone, ip, ipv6, user_agent, 
                os_type, os_version, browser, referrer, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, email, phone, ip, ipv6, user_agent, 
             os_type, os_version, browser, referrer, timestamp))
            conn.commit()
            conn.close()
            
            flash("Thank you for submitting your details!", "success")
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Error processing form: {str(e)}")
            flash("An error occurred while processing your request", "danger")
            return redirect(url_for('user_form'))
    
    return render_template('user_form.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('iplogs.db')
        c = conn.cursor()
        c.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = c.fetchall()
        conn.close()
        return render_template('admin.html', logs=logs)
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        flash("Could not retrieve logs", "danger")
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash("Invalid credentials", "danger")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('iplogs.db')
        c = conn.cursor()
        c.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        conn.commit()
        conn.close()
        flash("Log deleted successfully", "success")
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        flash("Could not delete log", "danger")
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Never run with debug=True in production!
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)