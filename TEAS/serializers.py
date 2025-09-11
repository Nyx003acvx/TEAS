from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Attendance, Employee


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ["id", "user", "employee_id", "phone", "department", "position"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        employee = Employee.objects.create(user=user, **validated_data)
        return employee


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee.user.get_full_name", read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "status",
            "check_in_time",
            "check_out_time",
            "latitude",
            "longitude",
            "created_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class AttendanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "employee",
            "date",
            "status",
            "latitude",
            "longitude",
            "check_in_time",
        ]
