from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True)
    link_clicks = models.IntegerField(default=0)
    filename = models.CharField(max_length=1000,blank=True)
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=("groups"),
        blank=True,
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=("user permissions"),
        blank=True,
        related_name="customuser_set",  # Unique related_name for user_permissions
        related_query_name="user",
    )

    def __str__(self):
        return self.username
    
    def check_clicks(self):
        if self.link_clicks > 0:
            return True
        return False
    
class Logs(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    filename = models.CharField(max_length=1000)


class PersonType(models.TextChoices):
    PARENT = 'Parent', 'Parent'
    TEACHER = 'Teacher', 'Teacher'
    OTHER_WORKER = 'OtherWorker', 'Other Worker'
    STUDENT = 'Student', 'Student'


class Teacher(models.Model):
    teachername = models.CharField(max_length=100, blank=True)
    user_id = models.UUIDField(blank=True, null=True)
    role = models.CharField(max_length=100, default='Teacher')
    image = models.ImageField(upload_to='profile_images/', blank=True)
    age = models.IntegerField(blank=True, null=True) 
    role = models.CharField(max_length=100, blank=True)
    form = models.ForeignKey('Form', on_delete=models.CASCADE, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    officialphone = models.CharField(max_length=100, blank=True)
    officialphonext = models.CharField(max_length=100, blank=True)
    logId = models.CharField(max_length=100, blank=True)
    imgurl = models.CharField(max_length=1000, blank=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.teachername
    
    
class Student(models.Model):
    user_id = models.UUIDField(blank=True, null=True)
    role= models.CharField(max_length=100, default='Student')
    age = models.IntegerField(blank=True, null=True) 
    form = models.ForeignKey('Form', on_delete=models.CASCADE, blank=True, null=True)
    Name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    momnumberone = models.CharField(max_length=100, blank=True)
    fathernumberone = models.CharField(max_length=100, blank=True)  
    momnumbertwo = models.CharField(max_length=100, blank=True)
    fathernumbertwo = models.CharField(max_length=100, blank=True)
    gaurdian = models.CharField(max_length=100, blank=True)
    gaurdianphoneone = models.CharField(max_length=100, blank=True)
    gaurdianphonetwo = models.CharField(max_length=100, blank=True)
    officialphonext = models.CharField(max_length=100, blank=True)
    logId = models.CharField(max_length=100, blank=True)
    imgurl = models.CharField(max_length=1000, blank=True)
    isActive = models.BooleanField(default=True)
    paycode = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.Name
    
class Parent(models.Model):
    user_id = models.UUIDField(blank=True, null=True)
    role = models.CharField(max_length=100, default='Parent')
    image = models.ImageField(upload_to='profile_images/', blank=True)
    imgurl = models.CharField(max_length=1000, blank=True)
    age = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True)
    phone2 = models.CharField(max_length=100, blank=True)
    parentname = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    logId = models.CharField(max_length=100, blank=True)
    createdAt = models.DateTimeField(blank=True, auto_now_add=True,null=True)
    isActive = models.BooleanField(default=True)
    trmpvisiting = models.CharField(max_length=1000,blank=True)
    
    def __str__(self):
        return self.parentname



class Form(models.Model):
    form_name = models.CharField(max_length=100, unique=True)
    form_description = models.CharField(max_length=100, blank=True)
    class_teacher = models.CharField(max_length=100, blank=True)
    directions = models.CharField(max_length=300, blank=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.form_name

    
class Attendance(models.Model):
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE,blank=True, null=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE,blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,blank=True, null=True)
    date = models.DateField(auto_now_add=True,blank=True, null=True)
    time = models.TimeField(auto_now_add=True,blank=True, null=True)
    status = models.BooleanField(default=False)
    reason = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(blank=True, null=True)
    checkout = models.TimeField(blank=True,null=True)
    islive = models.BooleanField(default=False)
    authType = models.CharField(max_length=100, blank=True,default='Face')
    authcode = models.CharField(max_length=100, blank=True)
    pid = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.user:
            return f"{self.user.teachername} - {self.date} - {self.status}"
        elif self.student:
            return f"{self.student.Name} - {self.date} - {self.status}"
        elif self.parent:
            return f"{self.parent.parentname} - {self.date} - {self.status}"
        else:
            return f"{self.date} - {self.status}"

class Pledge(models.Model):
    user = models.ForeignKey(Parent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    days_pledged = models.IntegerField()  
    pledge_date = models.DateField(auto_now_add=True)
    payment_made = models.BooleanField(default=False) 
    fulfilled_on = models.DateField(null=True, blank=True) 

class Transactions(models.Model):
    class Meta:
        verbose_name = ("Transaction")
        verbose_name_plural = ("Transactions")
    id=models.IntegerField(primary_key=True)
    amountpaid=models.IntegerField()
    RecieptNumber=models.IntegerField()
    payment_date=models.DateField(auto_now_add=True)
    payment_channel=models.CharField(max_length=200)
    PayCode=models.CharField(max_length=200)
    student=models.ForeignKey(Student,on_delete=models.SET_NULL,null=True, related_name='Student',blank=True)
    checked=models.BooleanField(default=False)
    def __str__(self):
      return self.PayCode
    