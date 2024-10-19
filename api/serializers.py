from rest_framework import serializers
from api.models import Notifications, tempOtp
from user.models import CustomUser, Logs, Teacher, Student, Parent, Form, Attendance, Pledge

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'link_clicks', 'filename', 'groups', 'user_permissions']

class LogsSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Logs
        fields = ['id', 'time_created', 'user', 'filename']

class TeacherSerializer(serializers.ModelSerializer):
    form = serializers.StringRelatedField()  # Shows the form name instead of ID

    class Meta:
        model = Teacher
        fields = [
            'id', 'teachername', 'user_id', 'role', 'image', 'age', 'form', 'phone', 'email', 
            'officialphone', 'officialphonext', 'logId', 'imgurl'
        ]

class StudentSerializer(serializers.ModelSerializer):
    form = serializers.StringRelatedField()  # Shows the form name instead of ID

    class Meta:
        model = Student
        fields = [
            'id', 'user_id', 'role', 'age', 'form', 'Name', 'phone', 'email', 'momnumberone',
            'fathernumberone', 'momnumbertwo', 'fathernumbertwo', 'gaurdian', 'gaurdianphoneone',
            'gaurdianphonetwo', 'officialphonext', 'logId', 'imgurl'
        ]

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
            'id', 'user_id', 'role', 'image', 'imgurl', 'age', 'phone', 'phone2', 'parentname', 
            'email', 'logId'
        ]

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id', 'form_name', 'form_description', 'class_teacher','directions', 'isActive']

class AttendanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), allow_null=True, required=False)
    parent = serializers.PrimaryKeyRelatedField(queryset=Parent.objects.all(), allow_null=True, required=False)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'parent', 'student', 'date', 'time', 'status', 'reason', 'rating', 
            'checkout', 'islive', 'pid'
        ]


class PledgeSerializer(serializers.ModelSerializer):
    user = ParentSerializer(read_only=True)

    class Meta:
        model = Pledge
        fields = ['id', 'user', 'amount', 'days_pledged', 'pledge_date', 'payment_made', 'fulfilled_on']



class TempOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = tempOtp
        fields = ['phone', 'otp', 'created_at','timestamp']


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'
