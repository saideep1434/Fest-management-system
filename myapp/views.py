from django.shortcuts import render
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
import datetime as date
from django.contrib import messages
from django.contrib.auth import logout
# Create your views here.
# views.py
import psycopg2
from psycopg2 import Error
from django.db import IntegrityError
from .models import *
from django.db import connection
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

def student_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        
        if(password != password1):
            error_message = "passwords not same."
            return render(request, 'myapp/register_student.html', {'error': error_message})
        # Raw SQL query to insert data into the Student table
        with connection.cursor() as cursor:

            cursor.execute("""
                    CREATE OR REPLACE FUNCTION insert_custom_user_student_trigger_function()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        INSERT INTO CustomUser (email, password, role)
                        VALUES (NEW.email, NEW.password, 'STUDENT');
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                    
                    DROP TRIGGER IF EXISTS insert_custom_user_student_trigger ON Student;

                    CREATE TRIGGER insert_custom_user_student_trigger
                    AFTER INSERT ON Student
                    FOR EACH ROW
                    EXECUTE FUNCTION insert_custom_user_student_trigger_function();
                """)
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Student (name, email, roll_number, password) VALUES (%s, %s, %s, %s)", [name, email, roll_number, password])
            
        except IntegrityError:
            error_message = "Email already exists. Please use a different email."
            return render(request, 'myapp/register_student.html', {'error': error_message})
        return redirect('myapp:login')
    else:
        return render(request, 'myapp/register_student.html',{'error': ''})


def external_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        college_name = request.POST.get('college_name')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        
        if(password != password1):
            error_message = "passwords not same."
            return render(request, 'myapp/register_external.html', {'error': error_message})

        # Raw SQL query to insert data into the Student table
        cursor=connection.cursor()

        cursor.execute("""
                create or replace function insert_custom_user_ep_trigger_function()
                returns trigger as $$
                begin
                    insert into CustomUser (email, password, role)
                    values (NEW.email, NEW.password,'EXTERNAL');
                    return NEW;
                end;
                $$ language plpgsql;
                
                drop trigger if exists insert_custom_user_ep_trigger ON ExternalParticipant;
                
                create trigger insert_custom_user_ep_trigger
                after insert on ExternalParticipant
                for each row
                execute function insert_custom_user_ep_trigger_function();
            """)
        try:
            cursor.execute("INSERT INTO ExternalParticipant (name, email, college_name, password) VALUES (%s, %s, %s, %s)", [name, email, college_name, password])
            #cursor.execute("INSERT INTO CustomUser (email, password, role) VALUES (%s, %s, %s)", [email, password,'EXTERNAL'])
        except IntegrityError:
            error_message = "Email already exists. Please use a different email."
            return render(request, 'myapp/register_external.html', {'error': error_message})
        #return HttpResponse("External Participantt registered successfully!")
        
        
        return redirect('myapp:login')
    else:
        return render(request, 'myapp/register_external.html',)
    
    
def organiser_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        if(password != password1):
            error_message = "passwords not same."
            return render(request, 'myapp/register_organiser.html', {'error': error_message})

        cursor = connection.cursor()

        cursor.execute("""
                    CREATE OR REPLACE FUNCTION insert_custom_user_org_trigger_function()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        INSERT INTO CustomUser (email, password, role)
                        VALUES (NEW.email, NEW.password, 'ORGANIZER');
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                    
                    drop trigger if exists insert_custom_user_org_trigger ON Organiser;

                    CREATE TRIGGER insert_custom_user_org_trigger
                    AFTER INSERT ON Organiser
                    FOR EACH ROW
                    EXECUTE FUNCTION insert_custom_user_org_trigger_function();
        """)
        
        try:
            cursor.execute("INSERT INTO Organiser (name, email,  password) VALUES (%s, %s,  %s)", [name, email, password])
            #cursor.execute("INSERT INTO CustomUser (email, password, role) VALUES (%s, %s, %s)", [email, password,'ORGANIZER'])
                
        except IntegrityError:
            error_message = "Email already exists. Please use a different email."
            return render(request, 'myapp/register_organiser.html', {'error': error_message})

        return redirect('myapp:login')

    else:
        return render(request, 'myapp/register_organiser.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Raw SQL query to verify email and password from CustomUser table
        with connection.cursor() as cursor:
            cursor.execute("SELECT email, password, role FROM CustomUser WHERE email = %s", [email])
            user_row = cursor.fetchone()

        if user_row is not None and user_row[1] == password:
            # Create a dictionary from the fetched row
            user_data = {'email': user_row[0], 'role': user_row[2]}
            request.session['student_email'] = email
            # Redirect to user-specific page based on role
            if user_data['role'] == 'STUDENT':
                return redirect('myapp:student_dashboard')
            elif user_data['role'] == 'EXTERNAL':
                return redirect('myapp:external_dashboard')
            elif user_data['role'] == 'ORGANIZER':
                return redirect('myapp:organizer_dashboard')
            elif user_data['role'] == 'ADMIN':
                return redirect('myapp:admin_dashboard')
        else:
            return render(request, 'myapp/login.html', {'error': 'Invalid email or password'})
    else:
        return render(request, 'myapp/login.html')
    
def add_user(request):
    return render(request, 'myapp/add_user.html')
    
def student_dashboard(request):
    #events = Event.objects.all()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Event")
        events_tuple = cursor.fetchall()
    events = [{'name': event[0], 'description': event[1], 'date': event[2], 'time': event[3], 'location': event[4]} for event in events_tuple]
    
    return render(request, 'myapp/student.html', {'events': events})
    #return render(request, 'myapp/student.html')
def external_dashboard(request):
    #events = Event.objects.all()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Event")
        events_tuple = cursor.fetchall()
    events = [{'name': event[0], 'description': event[1], 'date': event[2], 'time': event[3], 'location': event[4]} for event in events_tuple]
    
    return render(request, 'myapp/external.html',{'events': events})

def organizer_dashboard(request):
    #events = Event.objects.all()
    #volunteers = Volunteer.objects.all()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Event")
        events_tuple = cursor.fetchall()
    events = [{'name': event[0], 'description': event[1], 'date': event[2], 'time': event[3], 'location': event[4]} for event in events_tuple]
    
    return render(request, 'myapp/organiser.html',{'events': events})
    #return render(request, 'myapp/organizer.html')

def admin_dashboard(request):
    #users = CustomUser.objects.all()
    return render(request, 'myapp/admin.html')

from django.db import connection

def event_registration(request):
    if request.method == 'POST':
        event_name = request.POST.get('event')  # Extract event ID from the request
        student_email = request.session.get('student_email')  # Retrieve the student's email from the session

        # Execute an SQL INSERT query to add the event registration
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM EventRegistration WHERE student_email  = %s AND event = %s''',[student_email,event_name])
        check = cursor.fetchall()
        if len(check) == 0:
            cursor.execute("INSERT INTO EventRegistration (event, student_email) VALUES (%s, %s)", [event_name, student_email])
            messages.success(request, 'Registered successfully')
            #return HttpResponseRedirect(reverse('myapp:student_dashboard') + '?registered=' + event_name)  # Redirect back to the student dashboard after registration
        else:
            messages.warning(request, 'Already registered for this event.')
        return HttpResponseRedirect(reverse('myapp:student_dashboard') + '?registered=' + event_name)  # Redirect back to the student dashboard after registration
    else:
        return redirect('myapp:student_dashboard')  # If the request method is not POST, redirect to student dashboard
    
    
def event_ext_registration(request):
    if request.method == 'POST':
        event_name = request.POST.get('event')  # Extract event ID from the request
        student_email = request.session.get('student_email')  # Retrieve the student's email from the session

        # Execute an SQL INSERT query to add the event registration
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM EventRegistration WHERE student_email  = %s AND event= %s''',[student_email,event_name])
        check = cursor.fetchall()
        print(check)
        if len(check) == 0:
            cursor.execute("INSERT INTO EventRegistration (event, student_email) VALUES (%s, %s)", [event_name, student_email])
            messages.success(request, 'Registered successfully')
            #return HttpResponseRedirect(reverse('myapp:external_dashboard') + '?registered=' + event_name)  # Redirect back to the student dashboard after registration
        else:
            messages.warning(request, 'Already registered.')
        return HttpResponseRedirect(reverse('myapp:external_dashboard') + '?registered=' + event_name)
    else:
        return redirect('myapp:external_dashboard')  # If the request method is not POST, redirect to student dashboard
    
def accomadation_portal(request):
    cursor = connection.cursor()

    ep_mail = request.session.get('student_email')

    if ep_mail:
        # Fetch booked accommodation details for the logged-in user
        cursor.execute('''SELECT name_par, email, date, name_hall, price FROM Accomadation WHERE email = %s''', [ep_mail])
        booked_accommodation = cursor.fetchone()

        if booked_accommodation:
            # If accommodation is booked, construct a dictionary with the details
            booked_accommodation_details = {
                'name_par': booked_accommodation[0],
                'email': booked_accommodation[1],
                'date': booked_accommodation[2],
                'name_hall': booked_accommodation[3],
                'price': booked_accommodation[4]
            }
        else:
            # If no accommodation is booked, set booked_accommodation_details to None
            booked_accommodation_details = None

        return render(request, 'myapp/accomodation.html', {'booked_accommodation': booked_accommodation_details})
    else :
        return HttpResponse("External Participant email not found in session")

def hall_portal(request):
    cursor = connection.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Hall2(
                                name varchar(100),
                                location varchar(100),
                                vacancy int,
                                price int
            )''')

    cursor.execute('''INSERT INTO Hall2 (name, location, vacancy, price) VALUES (%s, %s, %s, %s)''', ["LBS HALL", "Old Hijili", 50, 200])
    cursor.execute('''INSERT INTO Hall2 (name, location, vacancy, price) VALUES (%s, %s, %s, %s)''', ["MT HALL", "Main Building", 50, 200])
    cursor.execute('''INSERT INTO Hall2 (name, location, vacancy, price) VALUES (%s, %s, %s, %s)''', ["SNVH HALL", "Pepsi Cut", 50, 200])
    cursor.execute('''INSERT INTO Hall2 (name, location, vacancy, price) VALUES (%s, %s, %s, %s)''', ["VS HALL", "Jhan Ghosh", 50, 200])
    cursor.execute('''INSERT INTO Hall2 (name, location, vacancy, price) VALUES (%s, %s, %s, %s)''', ["JCB HALL", "Gymkhana", 50, 200])

    cursor.execute('''INSERT INTO Hall (name, location, vacancy, price)
                        SELECT * FROM Hall2 as t2
                        WHERE NOT EXISTS (
                        SELECT *
                        FROM Hall as t1
                        WHERE t1.name = t2.name -- conditions to check for existence
    )''')

    cursor.execute('''DROP TABLE Hall2''')
    #return HttpResponse('table  created')
    
    cursor.execute("SELECT * FROM Hall")
    halls_tuple = cursor.fetchall()
    halls = [{'name': halls[0], 'location': halls[1], 'vacancy': halls[2], 'price': halls[3]} for halls in halls_tuple]
    
    return render(request, 'myapp/bookedhalls.html',{'halls': halls})
    #return render(request,'myapp/bookedhalls.html')


def volunteer_registration(request):
    if request.method == 'POST':
        # Retrieve student email from session
        student_email = request.session.get('student_email')
        event_name = request.POST.get('event')
        # Retrieve event object and student name
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM Student WHERE email = %s", [student_email])
            student_name = cursor.fetchone()[0]

            

        # Insert into Volunteer table using SQL query
        with connection.cursor() as cursor:
            cursor.execute('''SELECT * FROM Volunteer WHERE student_email  = %s AND event_name = %s''',[student_email,event_name])
            check = cursor.fetchall()
            if len(check) == 0:
                cursor.execute("INSERT INTO Volunteer (event_name, student_name, student_email) VALUES (%s, %s, %s)", [event_name, student_name, student_email])
                return HttpResponseRedirect(reverse('myapp:student_dashboard') + '?registered2=' + event_name)
            else:
                return HttpResponse("Already Volunteered for this event")
        # Redirect back to student dashboard or event page
        
    else:
        # Handle GET requests or other cases
        return redirect('myapp:student_dashboard')



def mybooking_portal(request):
    cursor = connection.cursor()

    if request.method == 'POST':
        name_hall = request.POST.get('name_hall')
        print("Name Hall:", name_hall)  # Debugging statement

        # Fetch email ID from session
        ep_mail = request.session.get('student_email')
        print("Email:", ep_mail)  # Debugging statement

        # Check if email ID is available in session
        if ep_mail:
            cursor.execute('''SELECT vacancy FROM Hall WHERE name = %s''', [name_hall])
            row = cursor.fetchone()
            print("Row:", row)  # Debugging statement

            cursor.execute('''SELECT * FROM Accomadation WHERE email = %s''', [ep_mail])
            sz=cursor.fetchall()
            print(sz)
            if len(sz) == 0:
                if row is not None:
                    vac = row[0]
                    if vac >= 0:
                        cursor.execute('''SELECT name, email FROM ExternalParticipant WHERE email = %s''', [ep_mail])
                        ep_info = cursor.fetchall()
                        print(ep_info)
                        list1 = []
                        current_date = datetime.date.today()

                        for i in range(len(ep_info[0])):
                            list1.append(ep_info[0][i])

                        list1.append(current_date)

                        cursor.execute('''SELECT name, price FROM Hall WHERE name = %s''', [name_hall])
                        hall_info = cursor.fetchall()

                        for i in range(len(hall_info[0])):
                            list1.append(hall_info[0][i])

                        print("List:", list1)  # Debugging statement
                        cursor.execute('''INSERT INTO Accomadation (name_par, email, date, name_hall, price) 
                                        VALUES (%s, %s, %s, %s, %s)''', list1)
                        vac = vac - 1
                        cursor.execute('''UPDATE Hall
                                        SET vacancy = %s
                                        WHERE name = %s''', [vac, name_hall])
                        cursor.execute('''SELECT name,location,vacancy, price FROM Hall WHERE name = %s''', [name_hall])
                        
                        
                        return render(request, 'myapp/payment.html')
                else:
                    return HttpResponse("No vacancies")
            else:
                return HttpResponse("More than one booking not allowed")
        else:
            return HttpResponse("External Participant email not found in session")
    else:
        return HttpResponse("Method not allowed")


def logout_view(request):
    logout(request)
    # Redirect to a specific URL after logout
    return redirect('myapp:homepage')


from django.db import connection


def event_details(request):
    if request.method == 'POST':
        event_name = request.POST.get('event')

        # Fetch participants' details using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("SELECT distinct customuser.email, student.name FROM customuser INNER JOIN eventregistration ON customuser.email = eventregistration.student_email INNER JOIN student ON student.email = eventregistration.student_email WHERE eventregistration.event = %s", [event_name])
            participants = cursor.fetchall()
            #print(participants)
        # Fetch volunteers' details using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("SELECT distinct customuser.email, student.name FROM customuser INNER JOIN volunteer ON customuser.email = volunteer.student_email INNER JOIN student ON student.email = volunteer.student_email WHERE volunteer.event_name = %s", [event_name])
            volunteers = cursor.fetchall()
            #print(volunteers)
        with connection.cursor() as cursor:
            cursor.execute("SELECT org_name FROM Event_has_organiser WHERE event_name = %s", [event_name])
            row = cursor.fetchone()
            org_name = row[0] if row else "No organizer assigned"

        return render(request, 'myapp/admin_event_details.html', {'participants': participants, 'volunteers': volunteers,'org_name': org_name})

    # Return an empty response for GET requests
    return render(request, 'myapp/event_details.html', {'participants': [], 'volunteers': [], 'org_name': org_name})

def event_details_org(request):
    if request.method == 'POST':
        event_name = request.POST.get('event')

        # Fetch participants' details using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("SELECT distinct customuser.email, student.name FROM customuser INNER JOIN eventregistration ON customuser.email = eventregistration.student_email INNER JOIN student ON student.email = eventregistration.student_email WHERE eventregistration.event = %s", [event_name])
            participants = cursor.fetchall()
            #print(participants)
        # Fetch volunteers' details using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("SELECT distinct customuser.email, student.name FROM customuser INNER JOIN volunteer ON customuser.email = volunteer.student_email INNER JOIN student ON student.email = volunteer.student_email WHERE volunteer.event_name = %s", [event_name])
            volunteers = cursor.fetchall()
            #print(volunteers)
        with connection.cursor() as cursor:
            cursor.execute("SELECT org_name FROM Event_has_organiser WHERE event_name = %s", [event_name])
            row = cursor.fetchone()
            org_name = row[0] if row else "No organizer assigned"

        return render(request, 'myapp/event_details.html', {'participants': participants, 'volunteers': volunteers,'org_name': org_name})

    # Return an empty response for GET requests
    return render(request, 'myapp/event_details.html', {'participants': [], 'volunteers': [], 'org_name': org_name})

def hall_admin_portal(request):
    
    cursor = connection.cursor()
    
    
    cursor.execute("SELECT * FROM Hall")
    halls_tuple = cursor.fetchall()
    halls = [{'name': halls[0], 'location': halls[1], 'vacancy': halls[2], 'price': halls[3]} for halls in halls_tuple]
    
    return render(request, 'myapp/hall_admin.html',{'halls': halls})
    #return render(request,'myapp/bookedhalls.html')
    
def hall_details(request):
    if request.method == 'POST':
        name_hall = request.POST.get('name_hall')
        
        # Fetch participants for the specified hall using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT email, name_par 
                FROM accomadation 
                WHERE name_hall =  %s
                
            """, [name_hall])
            participants = cursor.fetchall()
            print(participants)
        return render(request, 'myapp/hall_details.html', {'name_hall': name_hall, 'participants': participants})
    else:
        return HttpResponse("Method not allowed")
    
def admin_event_dashboard(request):
    #events = Event.objects.all()
    #volunteers = Volunteer.objects.all()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Event")
        events_tuple = cursor.fetchall()
    events = [{'name': event[0], 'description': event[1], 'date': event[2], 'time': event[3], 'location': event[4]} for event in events_tuple]
    
    return render(request, 'myapp/admin_event.html',{'events': events})
    #return render(request, 'myapp/organizer.html')
    
def contact(request):
    return render(request, 'myapp/contact.html')
def sponsor(request):
    return render(request, 'myapp/sponsors.html')

def homepage(request):
    with connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE  IF NOT EXISTS Student(
                            name varchar(100),
                            email varchar(100),
                            roll_number varchar(20),
                            password varchar(100),
                            PRIMARY KEY(email)
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS ExternalParticipant(
                        name varchar(100),
                        email varchar(100),
                        college_name varchar(20),
                        password varchar(100),
                        PRIMARY KEY(email)
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Organiser(
                        name varchar(100),
                        email varchar(100),
                        password varchar(100),
                        PRIMARY KEY(email)
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS CustomUser (
                            email VARCHAR(100),
                            password VARCHAR(100),
                            role VARCHAR(100)

            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS EventRegistration(
                            event varchar(200),
                            student_email varchar(100) 
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Accomadation(
                        name_par varchar(100),
                        email varchar(100),
                        date DATE,
                        name_hall varchar(100),
                        price int,
                        FOREIGN KEY (email) REFERENCES ExternalParticipant (email) ON DELETE CASCADE                  
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Hall(
                        name varchar(100),
                        location varchar(100),
                        vacancy int,
                        price int
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Hall2(
                                name varchar(100),
                                location varchar(100),
                                vacancy int,
                                price int
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Volunteer(
                        event_name varchar(100),
                        student_name varchar(100),
                        student_email varchar(100),
                        FOREIGN KEY (student_email) REFERENCES Student (email) ON DELETE CASCADE,
                        primary key(event_name,student_name,student_email)
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Winners(
                           event varchar(200),
                           name_par varchar(100),
                           email varchar(100)           
            )''')
    return render(request, 'myapp/homepage.html')


def winner(request):
    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute('''SELECT name FROM Event''')
        check = cursor.fetchall()
        events=[]
        for i in range(len(check)):
            events.append(check[i][0])
        

        winners=[]
        for i in range(len(events)):
            cursor.execute('''SELECT student_email FROM  EventRegistration WHERE event = %s''',[events[i]])
            smail=cursor.fetchall()
            
            cursor.execute('''SELECT name FROM ExternalParticipant WHERE email = %s''',[smail[0][0]])
            check_ep=cursor.fetchall()
            cursor.execute('''SELECT name FROM Student WHERE email = %s''',[smail[0][0]])
            check_std = cursor.fetchall()

            if(len(check_ep)!=0):
                l=[events[i],check_ep[0][0],smail[0][0]]
                winners.append(l)
            elif (len(check_std)!=0):
                l=[events[i],check_std[0][0],smail[0][0]]
                winners.append(l)

        cursor.execute('''SELECT * FROM Winners''')
        check=cursor.fetchall()
        if(len(check)<len(events)):
            for i in range(len(winners)):
                cursor.execute('''INSERT INTO Winners (event,name_par,email) VALUES (%s, %s,  %s)''',[winners[i][0],winners[i][1],winners[i][2]])
    return render(request,'myapp/winner.html',{'winners':winners})       
    #return redirect('myapp:homepage')
    
def delete(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        cursor = connection.cursor()
        cursor.execute('''SELECT role FROM CustomUser WHERE email = %s''',[email])
        role=(cursor.fetchall())[0][0]
        print(role)
        cursor.execute('''DELETE FROM Customuser WHERE email = %s''',[email])

        if role == 'STUDENT':
            cursor.execute('''DELETE FROM Student WHERE email = %s''',[email])
            cursor.execute('''SELECT * FROM EventRegistration WHERE student_email  = %s''',[email])
            check=cursor.fetchall()
            if(len(check)!=0):
                cursor.execute('''DELETE FROM EventRegistration WHERE student_email  = %s''',[email])
            cursor.execute('''SELECT * FROM Winners WHERE email  = %s''',[email])
            check=cursor.fetchall()
            if(len(check)!=0):
                cursor.execute('''DELETE FROM Winners WHERE email  = %s''',[email])
            return redirect('myapp:admin_dashboard')
        if role == 'EXTERNAL':
            cursor.execute('''SELECT * FROM Accomadation WHERE email  = %s''',[email])
            check=cursor.fetchall()
            if (len(check)!=0):
                cursor.execute('''SELECT name_hall FROM Accomadation WHERE email  = %s''',[email])
                name_hall=(cursor.fetchall())[0][0]
                cursor.execute('''SELECT vacancy FROM Hall WHERE name  = %s''',[name_hall])
                vac=(cursor.fetchall())[0][0]
                print(vac)
                vac=vac+1
                cursor.execute('''UPDATE Hall
                                        SET vacancy = %s
                                        WHERE name = %s''', [vac, name_hall])

            cursor.execute('''DELETE FROM ExternalParticipant WHERE email = %s''',[email])
            cursor.execute('''SELECT * FROM EventRegistration WHERE student_email  = %s''',[email])
            check=cursor.fetchall()
            if(len(check)!=0):
                cursor.execute('''DELETE FROM EventRegistration WHERE student_email  = %s''',[email])
            cursor.execute('''SELECT * FROM Winners WHERE email  = %s''',[email])
            check=cursor.fetchall()
            if(len(check)!=0):
                cursor.execute('''DELETE FROM Winners WHERE email  = %s''',[email])
            return redirect('myapp:admin_dashboard')
            
            
        if role == 'ORGANIZER':
            cursor.execute('''DELETE FROM Organizer WHERE email = %s''',[email])
            return redirect('myapp:admin_dashboard')

        else :
            return HttpResponse('No such user.')