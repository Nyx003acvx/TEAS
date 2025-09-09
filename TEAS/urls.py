from django.urls import path

from . import views

urlpatterns = [
    # API endpoints
    path("api/create-user/", views.create_user, name="create_user"),
    path("api/users/", views.get_users, name="get_users"),
    path("api/mark-attendance/", views.mark_attendance, name="mark_attendance"),
    path("api/get-attendances/", views.get_attendances, name="get_attendances"),
    # Web views
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("mark-attendance/", views.mark_attendance_form, name="mark_attendance_form"),
    path("attendance-summary/", views.attendance_summary, name="attendance_summary"),
]
