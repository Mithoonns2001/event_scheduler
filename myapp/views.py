from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError
from datetime import datetime
from django.http import HttpResponseForbidden
from .models import *
import bcrypt
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        errors = User.objects.Validate_Registration(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        # Create a user
        new_user = User.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            password=hashed_pw,
            role=request.POST['role'],
            # secret_password=request.POST['secret_password']

        )
        # Create a session
        request.session['user_id'] = new_user.id
        if new_user.role=='employee':
            redirect_url = f'/user/{new_user.id}/events_list'
            return redirect(redirect_url)
        if new_user.role=='head':
            redirect_url = f'/head/events_list'
            return redirect(redirect_url)
    return redirect('/head/events_list')


# def employee_dashboard(request):
#     user_id = request.session.get('user_id')
#     if user_id:
#         user = User.objects.get(id=user_id)
#         name = user.first_name
#     return redirect('/employee_dashboard')
    
def login(request):
    if request.method == 'POST':
        log_email = request.POST['log_email']
        log_password = request.POST['log_password']
        log_role = request.POST['log_role']
        print(log_role)
        try:
            user = User.objects.get(email=log_email, role=log_role)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password 2')
            return redirect('/')

        if bcrypt.checkpw(log_password.encode(), user.password.encode()):
        # Store user_id in session
            request.session['user_id'] = user.id

            # Construct the redirect URL based on the user's role
            if log_role == 'employee':
                redirect_url = f'/user/{user.id}/events_list'
            elif log_role == 'head':
                redirect_url = f'/head/events_list'

            return redirect(redirect_url)


    return redirect('/')



def events_list_user(request, user_id):
    events = Event.objects.all()
    return render(request, 'user_dashboard.html', {'events': events, 'user_id': user_id})

def events_list_head(request):
    events = Event.objects.all()
    return render(request, 'admin_dashboard.html', {'events': events})

def admin_register(request):
    events = Event.objects.all()
    return render(request, 'admin_register.html', {'events': events})

# def schedule_event(request):
#     if request.method == 'POST':
#         name = request.POST['name']
#         description = request.POST['description']
#         dates_str = request.POST['dates'].strip()  # Remove leading and trailing spaces
#         dates_list = dates_str.split(',')  # Split the input by commas
        
#         # Validate and parse each date
#         parsed_dates = []
#         for date_str in dates_list:
#             try:
#                 parsed_date = datetime.strptime(date_str.strip(), '%d-%m-%Y').date()
#                 if parsed_date is None:
#                     raise ValidationError(f"Invalid date format: {date_str}.")
#                 parsed_dates.append(parsed_date)
#             except ValidationError as e:
#                 return render(request, 'schedule_event.html', {'error': e.message})

#         # Create event and event dates
#         event = Event.objects.create(name=name, description=description)
#         for date in parsed_dates:
#             EventDate.objects.create(event=event, date=date)

#         return redirect('events_list')

#     return render(request, 'schedule_event.html')
def schedule_event(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        image = request.FILES.get('image')  
        dates_str = request.POST['dates'].strip()  
        dates_list = dates_str.split(',')  

        # Validate and parse each date
        parsed_dates = []
        for date_str in dates_list:
            try:
                parsed_date = datetime.strptime(date_str.strip(), '%d-%m-%Y %H:%M')  
                parsed_dates.append(parsed_date)
            except ValueError:
                return render(request, 'schedule_event.html', {'error': f"Invalid date format: {date_str}. Please use the format 'dd-mm-yyyy hh:mm'."})

        # Create event and event dates
        event = Event.objects.create(name=name, description=description, image=image)
        for date in parsed_dates:
            EventDate.objects.create(event=event, datetime=date) 

        return redirect('events_list')

    return render(request, 'schedule_event.html')

def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        event.name = request.POST.get('name')
        event.description = request.POST.get('description')
        event.save()

        dates_str = request.POST.get('dates').strip()
        dates_list = [date.strip() for date in dates_str.split(',')]
        event.eventdate_set.all().delete()  
        
        for date_str in dates_list:
            if date_str:
                date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')  
                EventDate.objects.create(event=event, datetime=date)  


        return redirect('events_list')

    return render(request, 'edit_event.html', {'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.delete()
        return redirect('events_list')
    else:
        return HttpResponseForbidden()
    
def vote_date(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        selected_date_id = request.POST.get('selected_date')
        selected_date = get_object_or_404(EventDate, pk=selected_date_id)
        selected_date.votes += 1
        selected_date.save()
        return redirect('events_list')
    return render(request, 'vote_date.html', {'event': event})



def vote_date_user(request, user_id, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        selected_date_id = request.POST.get('selected_date')
        selected_date = get_object_or_404(EventDate, pk=selected_date_id)
        
        # Check if the user has already voted for this event
        existing_vote = Vote.objects.filter(user_id=user_id, event_id=event_id).exists()
        if existing_vote:
            # messages.warning(request, "You have already voted for this event.")
            return redirect('events_list_user', user_id=user_id)
        
        Vote.objects.create(user_id=user_id, event_id=event_id, event_date=selected_date)
        
        # Increment the votes 
        selected_date.votes += 1
        selected_date.save()
        
        return redirect('events_list_user', user_id=user_id)
    
    return render(request, 'vote_date_user.html', {'event': event})
    
# def vote_date_user(request, user_id, event_id):
#     event = get_object_or_404(Event, pk=event_id)
#     user = get_object_or_404(User, pk=user_id)  # Assuming you have a User model

#     if request.method == 'POST':
#         selected_date_id = request.POST.get('selected_date')
#         selected_date = get_object_or_404(EventDate, pk=selected_date_id)
        
#         # Check if the user has already voted for this event
#         existing_vote = Vote.objects.filter(user_id=user_id, event_id=event_id).exists()
#         if existing_vote:
#             # Redirect with a message indicating that the user has already voted
#             return redirect('events_list_user', user_id=user_id)
        
#         # Create a new vote
#         vote = Vote.objects.create(user_id=user_id, event_id=event_id, event_date=selected_date)
        
#         # Increment the votes for the selected date
#         selected_date.votes += 1
#         selected_date.save()
        
#         # Send email notification to the user
#         subject = 'Vote Confirmation'
#         html_message="registered event"
#         # html_message = render_to_string('email/vote_confirmation.html', {'user': user, 'event': event, 'vote': vote})
#         plain_message = strip_tags(html_message)
#         from_email = 'mithoon.nagarajan@agilisium.com'  # Update with your email address
#         to_email = [user.email]
#         send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        
#         # Redirect to the events list for the specific user
#         return redirect('events_list_user', user_id=user_id)
    
#     return render(request, 'vote_date_user.html', {'event': event})

def notification_view(request):
    # Retrieve recent votes
    recent_votes = Vote.objects.order_by('-voted_at')[:20]
    return render(request, 'notification.html', {'recent_votes': recent_votes})

def logout(request):
    request.session.flush()
    return redirect('/')

def index(request):
    return render(request, 'index.html')