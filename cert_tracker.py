from flask import Flask, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
import threading
import time
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

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

db.create_all()

def schedule_reminders():
    while True:
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
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Register">
        </form>
    '''

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
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

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
    reminder_thread = threading.Thread(target=schedule_reminders, daemon=True)
    reminder_thread.start()
    app.run(debug=True)
