from django import forms

from .models import Attendance


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["status", "check_in_time", "check_out_time", "latitude", "longitude"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in_time": forms.TimeInput(attrs={"type": "time"}),
            "check_out_time": forms.TimeInput(attrs={"type": "time"}),
        }
