from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.models import Attendance, Teacher
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user.models import Parent
from .serializers import ParentSerializer
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import ClearenceCode, Parent
from .serializers import ParentSerializer

@api_view(['POST'])
def sync_attendance(request):
    data = request.data
    print(data)
  
    duplicate_query = {
        'date': data['date'],
        'student_id': data.get('student_id'),
    }


    existing_attendance = Attendance.objects.filter(**duplicate_query).exists()
    if existing_attendance:
        return Response({'error': 'Attendance record already exists for this date and student.'}, status=status.HTTP_400_BAD_REQUEST)
    user_id = request.data.get("user_id")
    parent  = request.data.get("parent")
    student = request.data.get("student")
    date = request.data.get("date")
    time =request.data.get("time")
    reason = request.data.get("reason")
    rating = request.data.get("rating")
    authType = request.data.get("authType")
    trmpvisiting = request.data.get("trmpvisiting")
    student_instance = None
    parent_instance = None

    print(parent)
    if parent:
        parent_instance = Parent.objects.filter(user_id=parent).first()
    else:
        parent_instance = None

    if student:
        student_instance = Teacher.objects.filter(user=student).first()
    else:
        student_instance = None
    print(parent_instance)
    print(student_instance)
    attendance_record = Attendance(
        user_id=data.get('user_id'),
        parent=parent_instance,
        student=student_instance,
        date=date,
        time=time,
        status=data['status'],
        reason=reason,
        rating=rating,
        checkout=data.get('checkout', None),
        authType=data.get('authType', 'Face'),
        authcode=data.get('authcode', ''),
        islive=data.get('islive', False),
        pid=data.get('pid', ''),
        trmpvisiting=trmpvisiting
    )

    attendance_record.save()


    attendance_record.save()
    return Response({'message': 'Attendance synced successfully.'}, status=status.HTTP_201_CREATED)



from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Parent

@api_view(['POST'])
def sync_parents(request):
    data = request.data

    existing_parent = Parent.objects.filter(user_id=data.get('user_id')).first()

    if existing_parent:        
        return Response({'message': 'Parent record updated successfully.'}, status=status.HTTP_200_OK)


    new_parent = Parent(
        user_id=data.get('user_id'),
        role=data.get('role'),
        imgurl=data.get('image_url'),
        age=data.get('age'),
        phone=data.get('phone'),
        phone2=data.get('phone2'),
        parentname=data.get('parentname'),
        email=data.get('email'),
        logId=data.get('logId'),
    )

    new_parent.save()
    return Response({'message': 'Parent synced successfully.'}, status=status.HTTP_201_CREATED)




class FetchTodaysParentsView(APIView):
    serializer_class = ParentSerializer


    def get_queryset(self):
        today = timezone.now().date()
        return Parent.objects.all()

    def get(self, request, *args, **kwargs):
        parents = self.get_queryset()
        print(parents)
        serializer = self.serializer_class(parents, many=True)
        return Response(serializer.data)


class SyncTrmpVisiting(APIView):
    def post(self, request, *args, **kwargs):
        is_active = request.data.get("is_active")
        code = request.data.get("code")
        trmpvisiting = request.data.get("trmpvisiting")
        created = request.data.get("created")

        print(trmpvisiting)
        print(request.data)

        clearence = ClearenceCode.objects.filter(code=code).first()  # Use .first() to get an object, not a queryset
        
        if clearence:
            clearence.trmpvisiting = trmpvisiting
            clearence.is_active = is_active
            clearence.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Clearance code not found"}, status=status.HTTP_404_NOT_FOUND)
