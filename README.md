# Certification_Tracker
This app is created in flask and it can be used to track certifications.

# Certification Tracker App

## Overview
This is a Flask-based web application that allows users to register, log in, and manage certifications. Users can add certifications, view details, update them, and delete records. The app also features automated reminders for Continuing Education (CE) requirements, Annual Maintenance Fees (AMF), and certification expiration dates.

The app is intended to run locally on a server, such as a Rocky 9 server, and uses SQLite for data persistence.

## Features
- User Registration and Login System (with hashed passwords for security)
- Add, View, Update, and Delete Certifications
- Automatic Reminders for CE, AMF, and Certification Expiration Dates

## Prerequisites
- Python 3.7 or higher
- `pip` (Python package installer)

## Setup Instructions

1. **Clone or Download the Repository**
   - Save the Python script (`cert_tracker.py`) on your server.

2. **Install Dependencies**
   - Navigate to the directory containing the script and install the necessary packages:
     ```sh
     pip install flask flask_sqlalchemy werkzeug
     ```

3. **Run the Application**
   - Initialize the database and start the Flask app:
     ```sh
     python cert_tracker.py
     ```
   - The application should now be running locally on `http://127.0.0.1:5000`.

4. **Accessing the Application**
   - Open a web browser and go to `http://127.0.0.1:5000/register` to create an account.
   - After registering, you can log in at `http://127.0.0.1:5000/login`.

5. **Database Setup**
   - The SQLite database (`certifications.db`) is automatically created when you run the application for the first time.

## API Endpoints

### Authentication
- **Register**: `/register` (GET/POST)
  - Create a new user account.
- **Login**: `/login` (GET/POST)
  - Authenticate an existing user.
- **Logout**: `/logout` (GET)
  - Log out of the current session.

### Certifications
- **Add Certification**: `/certifications` (POST)
  - Adds a new certification. Requires a JSON body with the fields `name` and `earned_date` (in `YYYY-MM-DD` format).
- **View All Certifications**: `/certifications` (GET)
  - Lists all certifications for the logged-in user.
- **View Certification by ID**: `/certifications/<cert_id>` (GET)
  - View a specific certification by its ID.
- **Update Certification**: `/certifications/<cert_id>` (PUT)
  - Updates a certification. Requires a JSON body with the fields to be updated.
- **Delete Certification**: `/certifications/<cert_id>` (DELETE)
  - Deletes a certification by its ID.

## Running in Production
For production use, consider deploying this app on a cloud-based virtual machine (VM) such as AWS EC2, Google Cloud Compute Engine, or Azure Virtual Machines. Deploying to the cloud allows for scalability, remote access, and better reliability.

### Steps to Deploy on a Cloud-Based VM
1. **Set Up a Cloud VM**
   - Create a virtual machine on your cloud provider (e.g., AWS, GCP, Azure).
   - Choose an appropriate image (such as Ubuntu 20.04 or Rocky Linux 9) and ensure it has Python 3.7 or higher installed.

2. **Upload the Application**
   - Transfer the `cert_tracker.py` file to your VM using tools like SCP or SFTP.

3. **Install Dependencies**
   - SSH into your VM and navigate to the directory containing the script.
   - Install the necessary packages:
     ```sh
     pip install flask flask_sqlalchemy werkzeug
     ```

4. **Run the Application**
   - Run the application using Gunicorn for better performance:
     ```sh
     gunicorn -w 4 -b 0.0.0.0:5000 cert_tracker:app
     ```

5. **Set Up a Reverse Proxy**
   - Set up a web server like Nginx as a reverse proxy to forward requests to Gunicorn and to enable HTTPS.

6. **Database Considerations**
   - Instead of using SQLite, consider using a cloud-based database like AWS RDS, Google Cloud SQL, or Azure Database for PostgreSQL/MySQL for better reliability and scalability.

### Example Gunicorn Command
```sh
gunicorn -w 4 -b 0.0.0.0:5000 cert_tracker:app
```

## Security Considerations
- Change the `app.secret_key` to a strong, random value.
- Passwords are hashed using Werkzeug's `generate_password_hash()` for secure storage.
- Set up HTTPS for encrypted communication.

## Notes
- The app's automatic reminders run on a separate background thread. For production, consider using a dedicated task scheduler like Celery.
- The SQLite database (`certifications.db`) is used for local development and testing. You should migrate to a more robust database for production environments.

## Potential Improvements
- Add email notifications for upcoming CE, AMF, and certification expirations.
- Integrate a frontend for a more user-friendly experience.
- Enhance security with role-based access control (RBAC).

## License
This project is licensed under the GPLv3 License.

