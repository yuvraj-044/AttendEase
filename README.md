# AttendEAse — College Event Attendance Management System

AttendEAse is a Django-based web application designed to streamline the process of requesting and approving attendance for college events.

## Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)

## Quick Start Guide

Follow these steps to run the application in your external browser:

### 1. Open Terminal
Open your terminal application and navigate to the project root directory:
```bash
cd "/Users/yuvii/Documents/My Projects/AttendEAse"
```

### 2. Install Dependencies
Install the required Python packages (Django):
```bash
pip3 install -r requirements.txt
```

### 3. Run Migrations (Optional)
The database is already provided, but you can run this to ensure everything is up to date:
```bash
python3 manage.py migrate
```

### 4. Start the Development Server
Run the following command to start the server:
```bash
sh run.sh
```
*Tip: If you get a "Port already in use" error, you can run on a different port:*
```bash
sh run.sh 8001
```

### 5. Access the App
Open your favorite web browser (Chrome, Safari, Firefox, etc.) and go to:
**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** (or whichever port you chose).

---

## Troubleshooting

### Port already in use
If you see `Error: That port is already in use`, it means another process (likely another Django instance) is using port 8000. You have two options:

1. **Use a different port**:
   ```bash
   sh run.sh 8001
   ```
2. **Kill the process using port 8000**:
   ```bash
   lsof -t -i :8000 | xargs kill -9
   ```

---

## Accessing the Dashboard

### Test Users
The system already contains several test users. Since passwords are not provided, you can reset the password for any user using the terminal:

1. **Reset a student's password**:
   ```bash
   python3 manage.py changepassword yuvraj
   ```
2. **Create a new superuser** (for full admin access):
   ```bash
   python3 manage.py createsuperuser
   ```

### Roles and Dashboards
- **Students**: Can submit attendance requests for active events.
- **Event Coordinators**: Can create events and approve/reject student requests.
- **Class Teachers**: Perform final review and marking of attendance.

## Manual Changes Required
- **Port Binding**: If you want to access the app from another device on the same Wi-Fi network, run:
  ```bash
  python3 manage.py runserver 0.0.0.0:8000
  ```
  Then access it via `http://<your-ip-address>:8000/`.
