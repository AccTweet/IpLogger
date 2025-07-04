# Python IP Logger Tool

A modern, Matrix-inspired Flask web app for logging user details and connection info.  
Features a dark mode UI, admin authentication, accordion-style log viewing, and log deletion.

---

## Features

- **User lure form**: Collects name, email, and phone number.
- **Logs**: IP address (IPv4 or IPv6), user agent, OS, browser, referrer, and timestamp.
- **Admin dashboard**: Accordion-style log viewer with delete option.
- **Authentication**: Admin login required to view or delete logs.
- **Modern UI**: Matrix-style dark mode, responsive and full-screen.

---

## Requirements

- Python 3.7+
- Flask

---

## Installation

1. **Clone or download this repository.**

2. **Install dependencies:**
    ```bash
    pip install flask
    ```

3. **(Optional) Change the admin credentials and secret key:**
    - Edit `app.py` and set:
      ```python
      app.secret_key = 'your_strong_secret_key'
      ADMIN_USERNAME = 'your_admin_username'
      ADMIN_PASSWORD = 'your_admin_password'
      ```

---

## Usage

1. **Run the app:**
    ```bash
    python app.py
    ```
2. **Open your browser and visit:**
    - Home: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    - User Form: [http://127.0.0.1:5000/form](http://127.0.0.1:5000/form)
    - Admin Login: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)

---

## File Structure

```
.
├── app.py
└── templates/
    ├── admin.html
    ├── index.html
    ├── login.html
    └── user_form.html
```

---

## How It Works

- **User Form**:  
  Users fill in their name, email, and phone. On submit, the app logs:
  - Name, Email, Phone (from form)
  - IP address (as seen by the server)
  - IPv6 address (if used to connect)
  - User Agent (browser/device info)
  - OS Type, OS Version, Browser (parsed from User Agent)
  - Referrer (previous page)
  - Timestamp

- **Admin Dashboard**:  
  - Login required.
  - View all logs in an accordion interface.
  - Delete logs with a single click.

---

## Limitations

- **IMEI, device name, device model, local/private IP, DHCP info:**  
  Not possible to collect from a browser for privacy and security reasons.
- **IP addresses:**  
  Only the public IP (as seen by your server) is logged.  
  If the user connects via IPv4, IPv6 will be empty, and vice versa.
- **OS/Browser detection:**  
  Parsed from the User Agent string, which may not always be precise.

---

## Security Notes

- **Change the default admin password and secret key before deploying.**
- **Do not expose this app to the public internet without proper security hardening.**
- **Inform users if you are collecting their data, as required by law in many jurisdictions.**

---

## Screenshots

> ![User Form](screenshots/user_form.png)  
> ![Admin Dashboard](screenshots/admin_dashboard.png)

---

## Security Reminder

- **The admin login/dashboard URL is not linked anywhere in the app for security. Admins must type it manually.**