from django.contrib import admin

from api.models import Receipt, tempOtp,ClearenceCode,Notifications

# Register your models here.
admin.site.register(tempOtp)
admin.site.register(ClearenceCode)
admin.site.register(Notifications)
admin.site.register(Receipt)