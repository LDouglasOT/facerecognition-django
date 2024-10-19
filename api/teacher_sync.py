from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import Student, Teacher
from .serializers import StudentSerializer, TeacherSerializer

class TeacherCreateView(APIView):

    def post(self, request, *args, **kwargs):
        

        serializer = TeacherSerializer(data=request.data)
        
        if serializer.is_valid():

            if Teacher.objects.filter(user_id=serializer.validated_data['user_id']).exists():
                return Response({'detail': 'Teacher already exists.'}, status=status.HTTP_409_CONFLICT)

  
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ClearenceCode
from django.utils import timezone
from django.shortcuts import get_object_or_404

class TodayClearanceCodesView(APIView):
    def get(self, request):
        today = timezone.now().date() 
        clearance_codes = ClearenceCode.objects.all()
        print(clearance_codes)

        serialized_codes = [{
            'code': code.code,
            'created_by': code.created_by.user_id, 
            'is_active': code.is_active,
            'date_created': code.date_created,
            'time_created': code.time_created,
            'visitor_name': code.visitor_name,
            'visitor_contact': code.visitor_contact,
            'visitor_relationship': code.visitor_relationship,
            'studentone': code.studentone,
            'studenttwo': code.studenttwo,
            'studentthree': code.studentthree,
            'studentfour': code.studentfour,
            'studentfive': code.studentfive,
            'studentsix': code.studentsix,
            'studentseven': code.studentseven,
            'reason': code.reason,
            'pid': code.pid,
            "trmpvisiting": code.trmpvisiting
        } for code in clearance_codes]

        return Response(serialized_codes, status=status.HTTP_200_OK)




class StudentListView(APIView):
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)