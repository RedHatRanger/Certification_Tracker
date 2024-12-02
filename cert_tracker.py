from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
import threading
import time
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production use

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certifications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    earned_date = db.Column(db.Date, nullable=False)
    ce_due_date = db.Column(db.Date, nullable=False)
    amf_due_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "earned_date": self.earned_date.strftime("%Y-%m-%d"),
            "ce_due_date": self.ce_due_date.strftime("%Y-%m-%d"),
            "amf_due_date": self.amf_due_date.strftime("%Y-%m-%d"),
            "expiration_date": self.expiration_date.strftime("%Y-%m-%d")
        }


# Ensure templates and static folders exist
if not os.path.exists("templates"):
    os.makedirs("templates")
if not os.path.exists("static"):
    os.makedirs("static")

# Sample HTML templates with CSS for a Visual theme
register_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
    <title>Register</title>
</head>
<body>
    <div class="container">
        <h1>Register</h1>
        <form method="post">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Register</button>
        </form>
        <a href="/login">Already have an account? Login here.</a>
    </div>
</body>
</html>
"""

login_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
    <title>Login</title>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form method="post">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <a href="/register">Don't have an account? Register here.</a>
    </div>
</body>
</html>
"""

# Sample CSS for Facebook-like theme
style_css = """
body {
    font-family: Arial, sans-serif;
    background-color: #f0f2f5;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}
.container {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    width: 300px;
    text-align: center;
}
.form-group {
    margin-bottom: 15px;
    text-align: left;
}
label {
    font-weight: bold;
}
input[type="text"], input[type="password"] {
    width: 100%;
    padding: 10px;
    margin-top: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
}
.btn {
    background-color: #1877f2;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    width: 100%;
}
.btn:hover {
    background-color: #155db2;
}
a {
    color: #1877f2;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
"""

# Save templates to the templates directory only if they do not already exist
if not os.path.exists("templates/register.html"):
    with open("templates/register.html", "w") as f:
        f.write(register_template)

if not os.path.exists("templates/login.html"):
    with open("templates/login.html", "w") as f:
        f.write(login_template)

# Save CSS to the static directory only if it does not already exist
if not os.path.exists("static/style.css"):
    with open("static/style.css", "w") as f:
        f.write(style_css)

def schedule_reminders():
    while True:
        with app.app_context():
            current_date = datetime.now().date()
            certifications = Certification.query.all()
        for cert in certifications:
            if cert.ce_due_date == current_date:
                print(f"Reminder: CE is due today for certification '{cert.name}' (ID: {cert.id})")
            if cert.amf_due_date == current_date:
                print(f"Reminder: AMF is due today for certification '{cert.name}' (ID: {cert.id})")
            if cert.expiration_date == current_date:
                print(f"Reminder: Certification '{cert.name}' (ID: {cert.id}) has expired today")
        time.sleep(86400)  # Check once every day

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            return redirect(url_for('get_certifications'))
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/certifications', methods=['POST'])
@login_required
def add_certification():
    data = request.get_json()
    name = data.get('name')
    earned_date_str = data.get('earned_date')
    earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
    ce_due_date = earned_date + timedelta(days=365 * 3)  # Assuming CE is due every 3 years
    amf_due_date = earned_date + timedelta(days=365)  # Assuming AMF is due annually from earned date
    expiration_date = earned_date + timedelta(days=365 * 5)  # Assuming certification expires after 5 years

    cert = Certification(name=name, earned_date=earned_date, ce_due_date=ce_due_date, amf_due_date=amf_due_date, expiration_date=expiration_date)
    db.session.add(cert)
    db.session.commit()
    return jsonify(cert.to_dict()), 201

@app.route('/certifications', methods=['GET'])
@login_required
def get_certifications():
    certifications = Certification.query.all()
    return jsonify([cert.to_dict() for cert in certifications]), 200

@app.route('/certifications/<int:cert_id>', methods=['GET'])
@login_required
def get_certification(cert_id):
    cert = Certification.query.get(cert_id)
    if cert is None:
        return jsonify({"error": "Certification not found"}), 404
    return jsonify(cert.to_dict()), 200

@app.route('/certifications/<int:cert_id>', methods=['PUT'])
@login_required
def update_certification(cert_id):
    data = request.get_json()
    cert = Certification.query.get(cert_id)
    if cert is None:
        return jsonify({"error": "Certification not found"}), 404

    cert.name = data.get('name', cert.name)
    earned_date_str = data.get('earned_date', cert.earned_date.strftime("%Y-%m-%d"))
    cert.earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
    cert.ce_due_date = cert.earned_date + timedelta(days=365 * 3)
    cert.amf_due_date = cert.earned_date + timedelta(days=365)
    cert.expiration_date = cert.earned_date + timedelta(days=365 * 5)
    db.session.commit()
    return jsonify(cert.to_dict()), 200

@app.route('/certifications/<int:cert_id>', methods=['DELETE'])
@login_required
def delete_certification(cert_id):
    cert = Certification.query.get(cert_id)
    if cert is None:
        return jsonify({"error": "Certification not found"}), 404
    db.session.delete(cert)
    db.session.commit()
    return jsonify({"message": "Certification deleted"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database tables within the app context
    reminder_thread = threading.Thread(target=schedule_reminders, daemon=True)
    reminder_thread.start()
    app.run(debug=True)
