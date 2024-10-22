from django.urls import path

from api.teacher_sync import StudentListView, TeacherCreateView, TodayClearanceCodesView
from user.views import add_clearance_code, delete_form, form_list_create
from .views import BOPpayJob, Checkfees, GetVisitorListAPIView, GetformListView, NotificationsListView, OTPVerifyView, PersonCreateAPIView, PledgeView, ReceiptListCreateView, SchoolpayJob, TransactionView, TransactionsListView, UploadImageView, UserImageCreateAPIView, AttendanceCreateAPIView,OTPLoginView, GetStudentsListView, sms
from .cron import *


urlpatterns = [
    path('persons/', PersonCreateAPIView.as_view(), name='person-create'),
    path('user-images/', UserImageCreateAPIView.as_view(), name='user-image-create'),
    path('attendance/', AttendanceCreateAPIView.as_view(), name='attendance-create'),
    path('getotp/', OTPLoginView.as_view(), name='get_otp'),
    path('verifyotp/', OTPVerifyView.as_view(), name='verify_otp'),
    path('visitor/', GetVisitorListAPIView.as_view(), name='visitor'),
    path('notifications/', NotificationsListView.as_view(), name='notifications-list'),
    path('students/', GetStudentsListView.as_view(), name='students'),
    path('upload-image/', UploadImageView.as_view(), name='upload_image'),
    path('sync-forms/', GetformListView.as_view(), name='sync-teachers'),
    path('receipts/', ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('sync_trmpvisiting/',SyncTrmpVisiting.as_view(),name="sync_trmpvisiting"),
    path("sync-attendance/", sync_attendance, name="sync-attendance"),
    path("sync-parents/", sync_parents, name="sync-parents"),
    path("sync-local-parents/", FetchTodaysParentsView.as_view(), name="sync-students"),
    path('teachers-sync/', TeacherCreateView.as_view(), name='create-teacher'),
    path('clearance_codes/', TodayClearanceCodesView.as_view(), name='today-clearance-codes'),
    path('students-sync/', StudentListView.as_view(), name='student-list'),
    path('add-clearance-code/', add_clearance_code, name='add-clearance-code'),
    path('forms/', form_list_create, name='form_list_create'),
    path('forms/<int:id>/delete/', delete_form, name='delete_form'),

    path('transactions/<int:student_id>/', TransactionView.as_view(), name='transaction-list'),
    path('pledges/<int:user_id>/', PledgeView.as_view(), name='pledge-list-create'),
    path('schoolpay-job/', SchoolpayJob.as_view(), name='schoolpay-job'),
    path('bop-pay-job/', BOPpayJob.as_view(), name='bop-pay-job'),
    path('transactions/', TransactionsListView.as_view(), name='transactions-list'),
    path('checkfees/',Checkfees.as_view(),name="Checkfees"),
    path('sms/',sms.as_view(),name="getform")
]
