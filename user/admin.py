from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Logs)
admin.site.register(Form)
admin.site.register(Teacher)
admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Transactions)
admin.site.register(Pledge)