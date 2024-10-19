"""
URL configuration for linkprotect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from nigga import settings
from user.views import *
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', getLink,name="home"),
    path('api/', include('api.urls')),
    path('/users', home,name="users"),

    path('delete/<int:user_id>', delete_user,name="delete_user"),
  
    path('accounts/login/', login_view, name='login'),
    path('super/<int:user_id>', make_user_superuser, name='super'),
    path('revoke/<int:user_id>', revoke_user_superuser, name='revoke'),
    path('logout/', logout_view, name='logout'),
    path('logs/', get_logs, name='logs'),
    path('loggers/<int:user_id>', get_user_logs, name='logs_id'),
    path('students/', Students, name='Students'),  
    path('attendance/', Attendances, name='Attendance'),
    path('teachers/', Teachers, name='Teachers'),
    path('parents', Parents, name='Parents'),
    path('reports/<uuid:user_id>/', user_report, name='user_report'),
    path('person/update/<uuid:id>/', edit_teacher, name='update_person'),
    path('clearence/',getClearenceCodes,name="codes"),
    path('create-form/', create_form, name='create_form'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)