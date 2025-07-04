from flask import Flask, request, render_template, redirect, url_for, session, flash
import datetime
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = 'change_this_secret_key'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'  # Change this!

# Database setup
def init_db():
    if not os.path.exists('iplogs.db'):
        conn = sqlite3.connect('iplogs.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            ip TEXT,
            ipv6 TEXT,
            user_agent TEXT,
            os_type TEXT,
            os_version TEXT,
            browser TEXT,
            referrer TEXT,
            timestamp DATETIME
        )''')
        conn.commit()
        conn.close()

init_db()

def parse_user_agent(ua):
    os_type = os_version = browser = "Unknown"
    if ua:
        if "Windows" in ua:
            os_type = "Windows"
            match = re.search(r'Windows NT ([\d\.]+)', ua)
            os_version = match.group(1) if match else "Unknown"
        elif "Mac OS X" in ua:
            os_type = "Mac OS X"
            match = re.search(r'Mac OS X ([\d_\.]+)', ua)
            os_version = match.group(1).replace('_', '.') if match else "Unknown"
        elif "Linux" in ua:
            os_type = "Linux"
        elif "Android" in ua:
            os_type = "Android"
            match = re.search(r'Android ([\d\.]+)', ua)
            os_version = match.group(1) if match else "Unknown"
        elif "iPhone" in ua or "iPad" in ua:
            os_type = "iOS"
            match = re.search(r'OS ([\d_]+)', ua)
            os_version = match.group(1).replace('_', '.') if match else "Unknown"
        if "Chrome" in ua:
            browser = "Chrome"
        elif "Firefox" in ua:
            browser = "Firefox"
        elif "Safari" in ua and "Chrome" not in ua:
            browser = "Safari"
        elif "Edge" in ua:
            browser = "Edge"
        elif "MSIE" in ua or "Trident" in ua:
            browser = "Internet Explorer"
    return os_type, os_version, browser

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def user_form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        ipv6 = request.remote_addr if ':' in request.remote_addr else ''
        user_agent = request.headers.get('User-Agent')
        referrer = request.headers.get('Referer')
        timestamp = datetime.datetime.now()
        os_type, os_version, browser = parse_user_agent(user_agent)
        conn = sqlite3.connect('iplogs.db')
        c = conn.cursor()
        c.execute('''INSERT INTO logs (name, email, phone, ip, ipv6, user_agent, os_type, os_version, browser, referrer, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (name, email, phone, ip, ipv6, user_agent, os_type, os_version, browser, referrer, timestamp))
        conn.commit()
        conn.close()
        flash("Thank you for submitting your details!", "success")
        return redirect(url_for('index'))
    return render_template('user_form.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('iplogs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = c.fetchall()
    conn.close()
    return render_template('admin.html', logs=logs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('iplogs.db')
    c = conn.cursor()
    c.execute("DELETE FROM logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()
    flash("Log deleted.", "success")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)