import json
import random
from django.http import JsonResponse
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import Parent, Student, Teacher, Attendance
from user.serializers import ClearenceCodeSerializer
from .serializers import *
import datetime
from .models import *
from rest_framework.permissions import IsAuthenticated
import uuid
import http.client
from firebase_admin import storage
from django.core.files.storage import default_storage
import firebase_admin
from firebase_admin import credentials
import os

service_account_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'twinbrook-12f84.appspot.com'  
    })

class PersonCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        person_type = request.data.get('person_type', 'OTHER_WORKER').upper()
        print("HIT THIS GROUND")
        serializer = None
        if person_type == 'TEACHER':
            print(person_type)
            serializer = TeacherSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
    
        elif person_type == 'STUDENT':
            print(person_type)
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)

        elif person_type == 'PARENT':
            print(person_type)
            serializer = ParentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)

        else:
            print(person_type)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        teachers = Teacher.objects.all()
        students = Student.objects.all()
        parents = Parent.objects.all()
        return Response({
            "teachers": TeacherSerializer(teachers, many=True).data,
            "students": StudentSerializer(students, many=True).data,
            "parents": ParentSerializer(parents, many=True).data,
        }, status=status.HTTP_200_OK)

    

class UserImageCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        role = request.data.get('role', '').upper()

        if not request.data.get('user_id') or not request.data.get('reason'):
            return Response({"error": "user_id and reason are required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            person = None
            if role == 'PARENT':
                person = Parent.objects.get(user_id=request.data['user_id'])
            elif role == 'STUDENT':
                person = Student.objects.get(user_id=request.data['user_id'])
            elif role == 'TEACHER':
                person = Teacher.objects.get(user_id=request.data['user_id'])
            else:
                return Response({"error": "Invalid role provided"}, status=status.HTTP_400_BAD_REQUEST)

            today = datetime.datetime.today()
            existing_attendance = None
            if role == 'TEACHER':
                existing_attendance = Attendance.objects.filter(user=person, date=today).first()
            elif role == 'STUDENT':
                existing_attendance = Attendance.objects.filter(student=person, date=today).first()
            elif role == 'PARENT':
                existing_attendance = Attendance.objects.filter(parent=person, date=today).first()

            if existing_attendance:
                serializer = AttendanceSerializer(existing_attendance)
                return Response({
                    "message": "Attendance already exists for today",
                    "attendance": serializer.data
                }, status=status.HTTP_200_OK)

   
            data = request.data.copy()
            data['date'] = today  


            if role == 'TEACHER':
                data['user'] = person 
            elif role == 'STUDENT':
                data['student'] = person
            elif role == 'PARENT':
                data['parent'] = person

   
            serializer = AttendanceSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Attendance created successfully",
                    "attendance": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                print("invalid serializer")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except (Parent.DoesNotExist, Student.DoesNotExist, Teacher.DoesNotExist):
            print("User not found")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        attendance = Attendance.objects.all()
        return Response(AttendanceSerializer(attendance, many=True).data, status=status.HTTP_200_OK)



class OTPLoginView(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        otp_values = [random.randint(100000, 999999) for _ in range(12)]
        print(otp_values)
        otp_values = str(otp_values[0])
        student = Student.objects.filter(phone=phone).first()
        if not student:
            return Response({"error": "Student not found","message":"This phone number is not connected on any student account at twinbrook, Tap the get help button"}, status=status.HTTP_404_NOT_FOUND)

        if not phone:
            return Response({"error": "Phone number is required","message":"Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        duplicate = tempOtp.objects.filter(phone=phone).first()
        if duplicate:
            duplicate.delete()
        
        try:    
                data = request.data.copy()
                data['otp'] = otp_values
                serializer = TempOtpSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                
                # conn = http.client.HTTPSConnection("app.esmsuganda.com")
                # headersList = {
                # "Accept": "*/*",
                # "Authorization": "Bearer ae7723e248188d5269bccbf2e88db4bb228d220eb47ecaa85bf287aaf6d081bcc595d962e8c842c857c04189277e6d5a",
                # "Content-Type": "application/json" 
                # }
                # payload = json.dumps({
                # "number":phone,
                # "message":f" Your twinbrook temporary security code is {otp_values}, it expires in 10 minutes",
                # })
                # print("sent to teacher")
                # conn.request("POST", "/api/v1/send-sms", payload, headersList)
                # response = conn.getresponse()
                # result = response.read()
                # print(result)
                # print(result.decode("utf-8"))

                phone = phone
                sms = f"Your twinbrook temporary security code is {otp_values}, it expires in 10 minutes"
                
                contextx = {
                    "msisdn": [phone],
                    "message": sms,
                    "username": "odysseytech",
                    "password": "NtWpD@6n&V7mTR"
                }
                response = requests.post("https://mysms.trueafrican.com/v1/api/esme/send", json=contextx)
                print(response.json())

                if response.json().get('code') == 200:
                    return Response({"message": "OTP message successfully sent","otp":otp_values}, status=200)
                else:
                    return Response({"message": "Failed to send OTP message", "head": "Error"}, status=400)



        except CustomUser.DoesNotExist:
            return Response({"error": "User not found","message":"This phone number is not connected on any student account at twinbrook"}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        otps = tempOtp.objects.all()
        return Response(TempOtpSerializer(otps, many=True).data, status=status.HTTP_200_OK)
    

import json
import random
import http.client
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import tempOtp 
from .serializers import TempOtpSerializer  
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404



def decode_access_token(token):
    try:
        print("Token")
        access_token = AccessToken(token)

        print(access_token)
        print("stopping here")
        user_id = access_token['user_id']
        parent = get_object_or_404(Parent, id=user_id)
        print("Parent is", parent.user_id)
        return parent
    except TokenError as e:
        print("Errors here:", str(e))
        return None
    
class OTPVerifyView(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        otp = request.data.get('otp')
        print(request.data)
        if not phone or not otp:
            print("phone or otp not provided")
            return Response({"error": "Phone number and OTP are required","message":"Phone number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj = tempOtp.objects.get(phone=phone)
            print(otp_obj.has_ten_minutes_passed())
               
            if otp_obj.otp == otp:

                    parent = Parent.objects.filter(phone=phone).first()
                    if(parent):
                        otp_obj.delete()
                        refresh = RefreshToken.for_user(parent)
                        return Response({
                        "message": "OTP verified successfully",
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "new":"old"
                    }, status=status.HTTP_200_OK)
                    else:
                        parent = Parent.objects.create(
                        user_id=uuid.uuid4(),
                        phone=phone
                        )
                        refresh = RefreshToken.for_user(parent)
                        otp_obj.delete()
                        return Response({
                        "message": "OTP verified successfully",
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "new":"new"
                        }, status=status.HTTP_200_OK)
            else:
                    otp_obj.delete()
                    print("Invalid OTP")
                    return Response({"error": "Invalid OTP provided","message":"Invalid otp code"}, status=status.HTTP_400_BAD_REQUEST)
        except tempOtp.DoesNotExist:
            print("doesnot exist")
            return Response({"error": "Invalid OTP provided","message":"OTP code not registered in our system, press resend code to get new a token"}, status=status.HTTP_400_BAD_REQUEST)

def getToken(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
        try:
            prefix, token = auth_header.split(' ')
            if prefix == 'Bearer':
                return token
            else:
                return None
        except ValueError:
            return None



class GetVisitorListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        print(request.data)
        
        token = request.data.get("token", None)  
        print("Received Token:", token)  
        parent = None
        if token:
            parent = decode_access_token(token=token)
        
        visitorname = request.data.get('name')
        phone = request.data.get('phone')
        visitorrelationship = request.data.get('visitor_relationship')
        reason = request.data.get('reason')
        studenttwo = request.data.get('students')
        relationship = request.data.get('relationship')
        allStudents = ""
        if len(studenttwo) > 0:
            for student in studenttwo:
                allStudents += student + ","
            
        otp_value = random.randint(10000000, 99999999)
        otp_value_str = str(otp_value)
        print(otp_value_str)
        
        created_by = request.data.get('created_ by')
        if not visitorname or not relationship or not reason:
            return Response({"message": "Some fields are missing"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:       
            visitor = ClearenceCode.objects.create(
                code=otp_value_str,
                visitor_name=visitorname,
                visitor_contact=phone,
                visitor_relationship=relationship,
                studentone=allStudents,
                studenttwo=studenttwo,
                reason=reason,
                created_by=parent
            )
            sms = f"{parent.parentname} has created twinbrook temporary security code is {otp_value_str}, it expires today , please don't share this code since onetime use"
            contextx = {
                "msisdn": [phone],
                "message": sms,
                "username": "odysseytech",
                "password": "NtWpD@6n&V7mTR"
            }
            response = requests.post("https://mysms.trueafrican.com/v1/api/esme/send", json=contextx)
            print(response.json())
            return Response({"message": "Visitor added successfully"}, status=status.HTTP_201_CREATED)
        
        except Parent.DoesNotExist:
            return Response({"message": "Invalid code provided"}, status=status.HTTP_400_BAD_REQUEST)
        

    def put(self, request, *args, **kwargs):
        token = request.data.get("token", None)  
        print("Received Token:", token)  
        print(request.data)
        print("/////////////////////////////////////////////")
        if token:
            parent = decode_access_token(token=token)
            print("Parent:", parent)
            if parent:
                codes = ClearenceCode.objects.filter(created_by=parent)
                serializers = ClearenceCodeSerializer(codes, many=True)
                return Response(serializers.data, status=status.HTTP_200_OK)
        
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
            

class NotificationsListView(APIView):
    def get(self, request):
        notifications = Notifications.objects.all()
        serializer = NotificationsSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetStudentsListView(APIView):
    def get(self, request):
        token = request.data.get("token", None)          
        parent = None
        if token:
            parent = decode_access_token(token=token)

        students = Student.objects.filter(phone=parent.phone)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class GetformListView(APIView):
    def get(self, request):
        form = Form.objects.all()
        serializer = FormSerializer(form, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UploadImageView(APIView):
    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        

        bucket = storage.bucket('twinbrook-12f84.appspot.com')
        blob = bucket.blob(image.name)
        blob.upload_from_file(image)
        blob.make_public() 

        return Response({'image_url': blob.public_url}, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        try:
            parentName=request.data.get("parentname")
            email=request.data.get("email")
            phone2=request.data.get("phone")
            imageUrl=request.data.get("imageUrl")
            token=request.data.get("token")
            print(token)
            if not token:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            parent = decode_access_token(token=token)

            if not parent:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            parent.parentname=parentName
            parent.phone2=phone2
            parent.email=email
            parent.imgurl=imageUrl
            parent.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        



# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Receipt
import json
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class ReceiptListCreateView(View):
    
    def get(self, request):
        receipts = Receipt.objects.all().values('id', 'reason', 'timestamp', 'user',"contact","students","image")
        return JsonResponse(list(receipts), safe=False)

    def post(self, request):

        data = json.loads(request.body)
        token = data.get('token')
        if not token:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        parent = decode_access_token(token=token)
        student = Student.objects.filter(phone=parent.phone)
        names = ""
        for s in student:
            names += s.Name + ","

        receipt = Receipt.objects.create(
            reason=data.get('reason'),
            user=parent.parentname,
            image = parent.imgurl,
            contact = parent.phone,
            students = names
        )
        return JsonResponse({'id': receipt.id, 'reason': receipt.reason, 'timestamp': receipt.timestamp, 'user': receipt.user, "contact":receipt.contact,"student":receipt.students,"image":receipt.image}, status=201)





# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from user.models import *
from django.contrib.auth.models import User
import json

@method_decorator(csrf_exempt, name='dispatch')
class TransactionView(View):
    def get(self, request, student_id):
        transactions = Transactions.objects.filter(student_id=student_id).values(
            'amountpaid', 'RecieptNumber', 'payment_date', 'payment_channel', 'PayCode', 'checked'
        )
        return JsonResponse(list(transactions), safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class PledgeView(View):
    def get(self, request, user_id):
        pledges = Pledge.objects.filter(user_id=user_id).values(
            'amount', 'days_pledged', 'pledge_date', 'payment_made', 'fulfilled_on'
        )
        return JsonResponse(list(pledges), safe=False)

    def post(self, request, user_id):
        data = json.loads(request.body)
        pledge = Pledge.objects.create(
            user_id=user_id,
            amount=data.get('amount'),
            days_pledged=data.get('days_pledged'),
        )
        return JsonResponse({
            'pledge_id': pledge.id,
            'amount': pledge.amount,
            'days_pledged': pledge.days_pledged,
            'pledge_date': pledge.pledge_date,
            'payment_made': pledge.payment_made,
            'fulfilled_on': pledge.fulfilled_on,
        }, status=201)

import hashlib


class SchoolpayJob(APIView):
    def get(self, request):
        today = datetime.date.today()
        value = today.strftime('%Y-%m-%d')
        code = "14001"
        password = 'tW!nI3r0Oktxn^&*(a0EWQ?"'
        fky = hashlib.md5(f"{code}{value}{password}".encode()).hexdigest()

        try:
            url = f"https://schoolpay.co.ug/paymentapi/AndroidRS/SyncSchoolTransactions/{code}/{value}/{fky}"
            response = requests.get(url)

            if response.status_code != 200:
                return Response({'message': 'Error'}, status=400)

            data = response.json()
            transactions = data.get('transactions', [])
            # print(transactions)
            for transaction in transactions:
                try:

                    if not Transactions.objects.filter(RecieptNumber=transaction['schoolpayReceiptNumber']).exists():

                        save_transaction = Transactions(
                            amountpaid=int(transaction['amount']),
                            RecieptNumber=int(transaction['schoolpayReceiptNumber']),
                            payment_channel=transaction['sourcePaymentChannel'],
                            PayCode=transaction['studentPaymentCode'],
                            payment_date=value,
                        )
                        save_transaction.save()
                except Exception as error:
                    print(f"Error processing transaction: {error}")

            return Response({'message': 'Success'})

        except Exception as error:
            return Response({'message': 'Error'}, status=500)
import datetime


class BOPpayJob(APIView):
    def get(self, request):
        today = datetime.date.today()
        value = today.strftime('%Y-%m-%d')
        code = "17534"
        password = 'g3Fqe^NEY8XCcn3g8W'
        fky = hashlib.md5(f"{code}{value}{password}".encode()).hexdigest()

        try:
            url = f"https://schoolpay.co.ug/paymentapi/AndroidRS/SyncSchoolTransactions/{code}/{value}/{fky}"
            response = requests.get(url)
            print(response)
            if response.status_code != 200:
                return Response({'message': 'Error'}, status=400)

            data = response.json()

            transactions = data.get('transactions', [])
            print(transaction)
            for transaction in transactions:
                try:

                    if not Transactions.objects.filter(RecieptNumber=transaction['schoolpayReceiptNumber']).exists():
         
                        save_transaction = Transactions(
                            amountpaid=int(transaction['amount']),
                            RecieptNumber=int(transaction['schoolpayReceiptNumber']),
                            payment_channel=transaction['sourcePaymentChannel'],
                            PayCode=transaction['studentPaymentCode'],
                            payment_date=value,
                        )
                        save_transaction.save()
                except Exception as error:
                    print(f"Error processing transaction: {error}")

            return Response({'message': 'Success'})

        except Exception as error:
            return Response({'message': 'Error'}, status=500)

class GetStudentsView(View):
    def post(self, request):
        token = request.GET.get('token')
        parent = decode_access_token(token=token)
        students = Student.objects.filter(phone=parent.phone).values('Name', 'phone')
        return JsonResponse(list(students.values()), safe=False) 



class TransactionsListView(APIView):
    def post(self, request):
        try:
            token = request.data.get('token')
            parent = decode_access_token(token=token)
            if parent is None:
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

            students = Student.objects.filter(phone=parent.phone)
            transactions = []
            for s in students:
                student_transactions = Transactions.objects.filter(student=s).values(
                    'amountpaid', 'payment_date', 'payment_channel', 'RecieptNumber', 'PayCode'
                )
                transactions.extend(list(student_transactions)) 

            return JsonResponse(transactions, safe=False, status=status.HTTP_200_OK)
        except Exception as e:

            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Checkfees(APIView):
    def post(self, request):
        print(request.data)
        phone = request.data.get("phone","")
        print(phone)
        students = Student.objects.filter(phone = phone)
        if len(students) == 0:
            return Response(status=200)
        
        st = ""
        total = 0
        paycode = []
        print(students)
        for s in students:
            print(s.Name)
            st += s.Name + " "
            total += s.payable
            paycode.append(s.paycode)

        transactions = Transactions.objects.filter(PayCode__in=paycode)
        totals = 0
        for t in transactions:
            totals += t.amountpaid

        return Response({"total":total, "names":st,'totals':totals},status=200)


class sms(APIView):
    def post(self,request):
        phone = request.data.get("phone")
        sms = request.data.get("sms")
        
        contextx = {
            "msisdn": [phone],
            "message": sms,
            "username": "odysseytech",
            "password": "NtWpD@6n&V7mTR"
        }
        response = requests.post("https://mysms.trueafrican.com/v1/api/esme/send", json=contextx)
        print(response.json())

        if response.json().get('code') == 200:
            return Response({"message": "OTP message successfully sent"}, status=200)
        
        else:

            return Response({"message": "Failed to send OTP message", "head": "Error"}, status=400)
        