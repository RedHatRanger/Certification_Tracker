from flask import Flask, request, jsonify, redirect, url_for, session, render_template, flash, url_for
from datetime import datetime, timedelta
import threading
import time
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'  # Change this for production use

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certifications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQLAlchemy logging for debugging

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

def schedule_reminders():
    while True:
        with app.app_context():
            current_date = datetime.now().date()
            certifications = Certification.query.order_by(Certification.earned_date.desc()).all()
            print(f"Certifications retrieved: {[cert.to_dict() for cert in certifications]}")  # Debug log
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
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User added: {new_user.username}")  # Debug log
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
            flash('Login successful!', 'success')
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
    if request.is_json:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON data"}), 400
        name = data.get('name')
        earned_date_str = data.get('earned_date')
    # Removed duplicate else block to fix syntax error
        ce_due_date_str = request.form.get('ce_due_date')
        amf_due_date_str = request.form.get('amf_due_date')
        expiration_date_str = request.form.get('expiration_date')

        try:
            ce_due_date = datetime.strptime(ce_due_date_str, "%Y-%m-%d")
            amf_due_date = datetime.strptime(amf_due_date_str, "%Y-%m-%d")
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('get_certifications'))
    else:
        name = request.form.get('name')
        earned_date_str = request.form.get('earned_date')

    if not name or not earned_date_str:
        flash('Invalid data. Please provide both name and earned date.', 'error')
        return redirect(url_for('get_certifications'))

    try:
        earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
        return redirect(url_for('get_certifications'))

    # If form data is used, ce_due_date is already set; otherwise, calculate from earned_date
    ce_due_date = ce_due_date if 'ce_due_date' in locals() else earned_date + timedelta(days=365 * 3)  # Assuming CE is due every 3 years
    # If form data is used, amf_due_date is already set; otherwise, calculate from earned_date
    amf_due_date = amf_due_date if 'amf_due_date' in locals() else earned_date + timedelta(days=365)  # Assuming AMF is due annually from earned date
    # If form data is used, expiration_date is already set; otherwise, calculate from earned_date
    expiration_date = expiration_date if 'expiration_date' in locals() else earned_date + timedelta(days=365 * 5)  # Assuming certification expires after 5 years

    cert = Certification(name=name, earned_date=earned_date, ce_due_date=ce_due_date, amf_due_date=amf_due_date, expiration_date=expiration_date)
    db.session.add(cert)
    db.session.commit()
    print(f"Certification added: {cert.to_dict()}")  # Debug log
    flash('Certification added successfully!', 'success')
    return redirect(url_for('get_certifications'))
    cert = Certification.query.get(cert_id)
    if cert is None:
        flash('Certification not found.', 'error')
        return redirect(url_for('get_certifications'))

    if request.method == 'POST':
        name = request.form.get('name')
        earned_date_str = request.form.get('earned_date')
        ce_due_date_str = request.form.get('ce_due_date')
        amf_due_date_str = request.form.get('amf_due_date')
        expiration_date_str = request.form.get('expiration_date')

        try:
            earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
            ce_due_date = datetime.strptime(ce_due_date_str, "%Y-%m-%d")
            amf_due_date = datetime.strptime(amf_due_date_str, "%Y-%m-%d")
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('get_certifications'))
        try:
            earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('update_certification', cert_id=cert_id))

        cert.name = name
        cert.earned_date = earned_date
        cert.ce_due_date = earned_date + timedelta(days=365 * 3)
        cert.amf_due_date = earned_date + timedelta(days=365)
        cert.expiration_date = earned_date + timedelta(days=365 * 5)
        db.session.commit()
        flash('Certification updated successfully!', 'success')
        return redirect(url_for('get_certifications'))
    name = data.get('name')
    earned_date_str = data.get('earned_date')
    try:
        earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    ce_due_date = earned_date + timedelta(days=365 * 3)  # Assuming CE is due every 3 years
    amf_due_date = earned_date + timedelta(days=365)  # Assuming AMF is due annually from earned date
    expiration_date = earned_date + timedelta(days=365 * 5)  # Assuming certification expires after 5 years

    cert = Certification(name=name, earned_date=earned_date, ce_due_date=ce_due_date, amf_due_date=amf_due_date, expiration_date=expiration_date)
    db.session.add(cert)
    db.session.commit()
    print(f"Certification added: {cert.to_dict()}")  # Debug log
    flash('Certification added successfully!', 'success')
    return jsonify(cert.to_dict()), 201

@app.route('/certifications', methods=['GET', 'POST'])
@login_required
def get_certifications():
    sort_by = request.args.get('sort_by', 'earned_date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Ensure sort_by is a valid column to prevent SQL injection
    valid_columns = ['name', 'earned_date', 'ce_due_date', 'amf_due_date', 'expiration_date']
    if sort_by not in valid_columns:
        sort_by = 'earned_date'

    # Use ascending or descending order based on sort_order parameter
    if sort_order == 'asc':
        certifications = Certification.query.order_by(getattr(Certification, sort_by).asc()).all()
    else:
        certifications = Certification.query.order_by(getattr(Certification, sort_by).desc()).all()

    if request.method == 'POST':
        # Handling new certification form submission
        name = request.form.get('name')
        earned_date_str = request.form.get('earned_date')
        try:
            earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('get_certifications'))
        ce_due_date = earned_date + timedelta(days=365 * 3)  # Assuming CE is due every 3 years
        amf_due_date = earned_date + timedelta(days=365)  # Assuming AMF is due annually from earned date
        expiration_date = earned_date + timedelta(days=365 * 5)  # Assuming certification expires after 5 years

        cert = Certification(name=name, earned_date=earned_date, ce_due_date=ce_due_date, amf_due_date=amf_due_date, expiration_date=expiration_date)
        db.session.add(cert)
        db.session.commit()
        flash('Certification added successfully!', 'success')
        return redirect(url_for('get_certifications'))

    return render_template('certifications.html', certifications=certifications, sort_by=sort_by, sort_order=sort_order)
    sort_by = request.args.get('sort_by', 'earned_date')
    sort_order = request.args.get('sort_order', 'desc')
    if sort_order == 'asc':
        certifications = Certification.query.order_by(getattr(Certification, sort_by).asc()).all()
    else:
        certifications = Certification.query.order_by(getattr(Certification, sort_by).desc()).all()
    if request.method == 'POST':
        name = request.form.get('name')
        earned_date_str = request.form.get('earned_date')
        try:
            earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('get_certifications'))
        ce_due_date = earned_date + timedelta(days=365 * 3)  # Assuming CE is due every 3 years
        amf_due_date = earned_date + timedelta(days=365)  # Assuming AMF is due annually from earned date
        expiration_date = earned_date + timedelta(days=365 * 5)  # Assuming certification expires after 5 years

        cert = Certification(name=name, earned_date=earned_date, ce_due_date=ce_due_date, amf_due_date=amf_due_date, expiration_date=expiration_date)
        db.session.add(cert)
        db.session.commit()
        flash('Certification added successfully!', 'success')
        return redirect(url_for('get_certifications'))

    certifications = Certification.query.order_by(Certification.earned_date.desc()).all()
    return render_template('certifications.html', certifications=certifications, sort_by=sort_by, sort_order=sort_order)
    certifications = Certification.query.order_by(Certification.earned_date.desc()).all()
    print(f"Certifications retrieved: {[cert.to_dict() for cert in certifications]}")  # Debug log
    return render_template('certifications.html', certifications=certifications)

@app.route('/certifications/<int:cert_id>', methods=['GET'])
@login_required
def get_certification(cert_id):
    cert = Certification.query.get(cert_id)
    if cert is None:
        return jsonify({"error": "Certification not found"}), 404
    return render_template('update_certification.html', certification=cert)

@app.route('/certifications/<int:cert_id>', methods=['GET', 'POST'])
@login_required
def update_certification(cert_id):
    cert = Certification.query.get(cert_id)
    if cert is None:
        flash('Certification not found.', 'error')
        return redirect(url_for('get_certifications'))

    if request.method == 'POST':
        name = request.form.get('name')
        earned_date_str = request.form.get('earned_date')
        ce_due_date_str = request.form.get('ce_due_date')
        amf_due_date_str = request.form.get('amf_due_date')
        expiration_date_str = request.form.get('expiration_date')

        try:
            earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
            ce_due_date = datetime.strptime(ce_due_date_str, "%Y-%m-%d")
            amf_due_date = datetime.strptime(amf_due_date_str, "%Y-%m-%d")
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('update_certification', cert_id=cert_id))

        cert.name = name
        cert.earned_date = earned_date
        cert.ce_due_date = ce_due_date
        cert.amf_due_date = amf_due_date
        cert.expiration_date = expiration_date
        db.session.commit()
        flash('Certification updated successfully!', 'success')
        return redirect(url_for('get_certifications'))

    return render_template('update_certification.html', certification=cert)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400
    cert = Certification.query.get(cert_id)
    if cert is None:
        return jsonify({"error": "Certification not found"}), 404

    cert.name = data.get('name', cert.name)
    earned_date_str = data.get('earned_date', cert.earned_date.strftime("%Y-%m-%d"))
    try:
        earned_date = datetime.strptime(earned_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    cert.ce_due_date = ce_due_date
    cert.amf_due_date = amf_due_date
    cert.expiration_date = expiration_date
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

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('get_certifications'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database tables within the app context
    reminder_thread = threading.Thread(target=schedule_reminders, daemon=True)
    reminder_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)  # Updated to work with Codespaces
