import json
from datetime import date, datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import logout as auth_logout

from .models import Attendance, Employee
from .serializers import (
    AttendanceCreateSerializer,
    AttendanceSerializer,
    EmployeeSerializer,
    UserSerializer,
)


# User Registration API
@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "user_id": user.id,
                "username": user.username,
                "message": "User created successfully",
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all users
@api_view(["GET"])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# Mark attendance
@api_view(["POST"])
def mark_attendance(request):
    serializer = AttendanceCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Check if attendance already exists for this employee on this date
        employee = serializer.validated_data["employee"]
        attendance_date = serializer.validated_data["date"]

        attendance, created = Attendance.objects.get_or_create(
            employee=employee, date=attendance_date, defaults=serializer.validated_data
        )

        if not created:
            # Update existing attendance record
            for attr, value in serializer.validated_data.items():
                setattr(attendance, attr, value)
            attendance.save()

        return Response(
            {
                "message": "Attendance marked successfully",
                "attendance_id": attendance.id,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all attendances for a specific date
@api_view(["GET"])
def get_attendances(request):
    date_param = request.GET.get("date")
    if date_param:
        try:
            attendance_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            attendances = Attendance.objects.filter(date=attendance_date)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        attendances = Attendance.objects.all()

    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)


# Attendance Summary View
@login_required
def attendance_summary(request):
    attendances = Attendance.objects.filter(employee__user=request.user).order_by(
        "-date"
    )
    return render(request, "TEAS/attendance_summary.html", {"attendances": attendances})


# Mark Attendance Form
@login_required
def mark_attendance_form(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            # Get employee object for current user
            try:
                employee = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return JsonResponse({"error": "Employee profile not found"}, status=400)

            # Create or update attendance
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=date.today(),
                defaults={
                    "status": "present",
                    "check_in_time": datetime.now().time(),
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )

            if not created:
                attendance.check_in_time = datetime.now().time()
                attendance.latitude = latitude
                attendance.longitude = longitude
                attendance.save()

            return JsonResponse({"message": "Attendance marked successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "TEAS/mark_attendance.html")


# Registration View
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        employee_id = request.POST["employee_id"]

        if User.objects.filter(username=username).exists():
            return render(
                request, "TEAS/register.html", {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

        Employee.objects.create(user=user, employee_id=employee_id)

        login(request, user)
        return redirect("mark_attendance_form")

    return render(request, "TEAS/register.html")


# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("mark_attendance_form")
        else:
            return render(request, "TEAS/login.html", {"error": "Invalid credentials"})

    return render(request, "TEAS/login.html")
