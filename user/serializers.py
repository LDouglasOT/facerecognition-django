from rest_framework import serializers
from .models import Form, Teacher, Student, Parent
from api.models import ClearenceCode  

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'teachername', 
            'image', 
            'user_id', 
            'role', 
            'image_url', 
            'age', 
            'form', 
            'phone', 
            'email', 
            'officialphone', 
            'officialphonext', 
            'logId'
        ]

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'user_id', 
            'profile_image_url', 
            'profile_image', 
            'role', 
            'age', 
            'form', 
            'Name', 
            'phone', 
            'email', 
            'momnumberone', 
            'fathernumberone', 
            'momnumbertwo', 
            'fathernumbertwo', 
            'gaurdian', 
            'gaurdianphoneone', 
            'gaurdianphonetwo', 
            'officialphonext', 
            'logId'
        ]

class ParentSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)  # Nest StudentSerializer for related students

    class Meta:
        model = Parent
        fields = [
            'user_id', 
            'role', 
            'image', 
            'students', 
            'imgurl', 
            'age', 
            'phone', 
            'phone2', 
            'parentname', 
            'email', 
            'logId'
        ]




class ClearenceCodeSerializer(serializers.ModelSerializer):
    created_by = ParentSerializer() 

    class Meta:
        model = ClearenceCode
        fields = [
            'id',
            'code',
            'created_by',
            'is_active',
            'date_created',
            'time_created',
            'visitor_name',
            'visitor_contact',
            'visitor_relationship',
            'studentone',
            'studenttwo',
            'studentthree',
            'studentfour',
            'studentfive',
            'studentsix',
            'studentseven',
            'reason'
        ]
        read_only_fields = ['id', 'date_created', 'time_created', 'created_by']

    def create(self, validated_data):
        parent = self.context['request'].user
        validated_data['created_by'] = parent
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('created_by', None) 
        return super().update(instance, validated_data)

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = '__all__'