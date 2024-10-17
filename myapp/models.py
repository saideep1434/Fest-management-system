from django.db import models
import datetime

# Create your models here.
class CustomUser(models.Model):
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=100)
    role_choices = [
        ('STUDENT', 'Student'),
        ('EXTERNAL', 'External_Participant'),
        ('ORGANIZER', 'Organizer'),
        ('ADMIN', 'Administrator')
    ]
    role = models.CharField(max_length=20, choices=role_choices)

class Student(models.Model):
    email = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    
class ExternalParticipant(models.Model):
    email = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    college_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    
class Organiser(models.Model):
    email = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class Event(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    description = models.TextField()
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200,blank=True, null=True)
    

    def __str__(self):
        return self.name
    
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student_email = models.EmailField()

    class Meta:
        unique_together = ('event', 'student_email')
        
class Hall(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    location = models.CharField(max_length=200,blank=True, null=True)
    vacancy = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

class Hall2(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    location = models.CharField(max_length=200,blank=True, null=True)
    vacancy = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

class Accomadation(models.Model):
    email = models.ForeignKey(ExternalParticipant, on_delete=models.CASCADE)
    name_par = models.CharField(max_length=100)
    name_hall = models.ForeignKey(Hall,on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    price = models.IntegerField(blank=True, null=True)
    
    
class Volunteer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_email = models.EmailField(blank=True, null=True)
    student_name = models.CharField(max_length=100,blank=True, null=True)  # Add student name field
    event_name = models.CharField(max_length=100,blank=True, null=True)   
    
class Event_has_organiser(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    organiser = models.ForeignKey(Organiser,on_delete = models.CASCADE)
    org_email = models.EmailField(blank=True, null=True)
    org_name = models.CharField(max_length=100,blank=True, null=True)  # Add student name field
    event_name = models.CharField(max_length=100,blank=True, null=True)  
    
class Winners(models.Model):
    event = models.CharField(max_length=200,primary_key=True)
    name_par = models.CharField(max_length=100)
    email = models.CharField(max_length=100)   
