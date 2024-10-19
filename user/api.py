from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Parent, Student, Teacher, Attendance
from .serializers import *
import datetime
from .models import *
import uuid

class PersonCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract data from the request
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        contact = request.data.get('phone')
        person_type = request.data.get('person_type', 'OTHER_WORKER').upper()
        email = request.data.get('email', '')
        officialphone = request.data.get('officialphone', '')
        officialphonext = request.data.get('officialphonext', '')
        profile_image = request.FILES.get('profile')
        students = request.data.get('students', '')
        imgurl = request.data.get('imgurl', '')
        print(request.data)
    
        if not name:
            return Response({'error': 'Name and profile image are required.'}, status=status.HTTP_400_BAD_REQUEST)
        print("HIT THIS GROUND")
        # Create the appropriate model instance based on person_type
        if person_type == 'TEACHER':
            print(person_type)
            person = Teacher.objects.create(
                user_id=user_id,
                teachername=name,
                phone=contact,
                email=email,
                imgurl=imgurl,
                )

        elif person_type == 'STUDENT':
            print(person_type)
            person = Student.objects.create(
                user_id=user_id,
                Name=name,
                phone=contact,
                email=email,
                imgurl = imgurl,
            )
            if students:
                person.students.set(students)

        elif person_type == 'PARENT':
            print(person_type)
            person = Parent.objects.create(
                user_id=user_id,
                parentname=name,
                phone=contact,
                email=email,
                imgurl=imgurl,
            )
        else:
            print(person_type)
            return Response({'error': 'Invalid person_type provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle the profile image if it's provided
        if profile_image:
            person.image = profile_image
            person.save()

        # Return the created person instance data
        response_data = {
            'user_id': person.user_id,
            'name': name,
            'profile': person.image.url if person.image else None,
            'person_type': person_type,
            'phone': person.phone,
            'email': person.email,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    

    

class UserImageCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AttendanceCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract data from request

        user_id = request.data.get('user_id')
        reason = request.data.get('reason')
        rating = request.data.get('rating', 0)
        islive = request.data.get('islive', True)
        time = request.data.get('time', datetime.datetime.now().strftime("%H:%M:%S"))
        date = request.data.get('date', datetime.date.today())
        time = request.data.get('time', datetime.datetime.now().strftime("%H:%M:%S"))
        role = request.data.get('role', '')
        print(request.data)
        if not user_id or not reason:
            return Response({"error": "user and reason are required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print(user_id)
            # Find the user in the Person model
            person = None
            if role == 'Parent':
                person = Parent.objects.get(user_id=user_id)
            elif role == 'Student':
                person = Student.objects.get(user_id=user_id)
                print(person.user_id)
            elif role == 'Teacher':
                person = Teacher.objects.get(user_id=user_id)
    

            # Check if attendance for today already exists
            today = datetime.date.today()

            existing_attendance = None
            if role == 'Teacher':
                existing_attendance = Attendance.objects.filter(user=person, date=today).first()
            elif role == 'Student':
                existing_attendance = Attendance.objects.filter(student=person, date=today).first()
            elif role == 'Parent':
                existing_attendance =Attendance.objects.filter(parent=person, date=today).first()
       

            if existing_attendance:
                return Response({
                    "message": "Attendance updated successfully",
                    "attendance": {
                        "user": existing_attendance.user.id,
                        "date": existing_attendance.date,
                        "time": existing_attendance.time,
                        "reason": existing_attendance.reason,
                        "rating": existing_attendance.rating,
                        "islive": existing_attendance.islive,
                    }
                }, status=status.HTTP_200_OK)
            else:
                # Create new attendance record if none exists
                if role == 'Teacher':
                    new_attendance = Attendance.objects.create(
                    user=person,
                    reason=reason,
                    rating=rating,
                    islive=islive,
                    time=time,
                    date=date,
                    )
                elif role == 'Student':
                    new_attendance = Attendance.objects.create(
                    student=person,
                    reason=reason,
                    rating=rating,
                    islive=islive,
                    time=time,
                    date=date,
                    )
                elif role == 'Parent':
                    new_attendance = Attendance.objects.create(
                    parent=person,
                    reason=reason,
                    rating=rating,
                    islive=islive,
                    time=time,
                    date=date,
                    )
              

                return Response({
                    "message": "Attendance created successfully",
                    "attendance": {
                    }
                }, status=status.HTTP_201_CREATED)

        except:
            print("User not found")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
