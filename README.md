# TEAS
# Tenvelop Employee Attendance System

## Features
- User registration and authentication
- Employee attendance marking with location capture
- Attendance records viewing
- REST API endpoints
- Location tracking using HTML5 Geolocation

## Setup Instructions
1. Install requirements: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Start server: `python manage.py runserver`

## API Endpoints
- POST /api/create-user/ - Create new user
- GET /api/users/ - Get all users
- POST /api/mark-attendance/ - Mark attendance
- GET /api/get-attendances/ - Get attendances

## Database Query

SQL query to retrieve all attendance records with employee information:
```
SELECT 
    a.id,
    u.first_name,
    u.last_name,
    e.employee_id,
    a.date,
    a.status,
    a.check_in_time,
    a.check_out_time,
    a.latitude,
    a.longitude,
    a.created_at
FROM TEAS_attendance a
JOIN TEAS_employee e ON a.employee_id = e.id
JOIN auth_user u ON e.user_id = u.id
ORDER BY a.date DESC, a.created_at DESC;

```
