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
   - Save the Python script (`certification_tracker_app.py`) on your server.

2. **Install Dependencies**
   - Navigate to the directory containing the script and install the necessary packages:
     ```sh
     pip install flask flask_sqlalchemy werkzeug
     ```

3. **Run the Application**
   - Initialize the database and start the Flask app:
     ```sh
     python certification_tracker_app.py
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
For production use, consider deploying this app using a WSGI server like Gunicorn and securing it behind a web server like Nginx. Update the `app.secret_key` to a strong, unique value and consider using a more robust database like PostgreSQL or MySQL.

### Example Gunicorn Command
```sh
gunicorn -w 4 -b 0.0.0.0:5000 certification_tracker_app:app
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

