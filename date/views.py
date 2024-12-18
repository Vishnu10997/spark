from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import profile1, Notification, ChatMessage
from django.http import JsonResponse
from django.db import models
from .forms import ProfileForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json

@login_required
def home(request):
    profiles = profile1.objects.exclude(user=request.user)
    current_index = request.session.get('current_profile_index', 0)

    if request.method == "POST":
        action = request.POST.get('action')
        profile = profiles[current_index]

        if action == "like":
            # Create a notification
            Notification.objects.create(
                recipient=profile.user,  # Ensure profile has a related user
                sender=request.user,
                message=f"{request.user.username} liked your profile!"
            )
        
        current_index += 1
        request.session['current_profile_index'] = current_index

        return redirect('home')

    if current_index >= len(profiles):
        return render(request, 'home.html', {'no_more_users': True})

    profile = profiles[current_index]
    return render(request, 'home.html', {'profile': profile, 'no_more_users': False})

@login_required
def redirect_to_chat_from_notification(request, notification_id):
    # Get the notification based on the ID and ensure it's for the current user
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    recipient_user = notification.sender  # Assuming the sender is the user who sent the notification

    # Redirect to the chat page with the recipient's user ID
    return redirect('chat', user_id=recipient_user.id)


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')  # Redirect to the notifications page

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': user_notifications})

@login_required
def profile(request):
    try:
        profile = profile1.objects.get(user=request.user)
    except profile1.DoesNotExist:
        profile = None  # Handle cases where the profile does not exist

    return render(request, 'profile.html', {'profile': profile})

from .forms import RegistrationForm
from random import randint
from django.core.mail import send_mail
otp_storage = {}
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save user but do not activate yet
            user = form.save(commit=False)
            user.is_active = False  # Prevent login until OTP verification
            user.save()

            # Generate OTP
            otp = str(randint(100000, 999999))
            otp_storage[user.username] = otp  # Save OTP in a temporary dictionary

            # Send OTP via email
            send_mail(
                'Your OTP Code',
                f'Hello {user.username}, your OTP is {otp}',
                'noreply@yourdomain.com',
                [user.email],
            )

            # Redirect to OTP verification page
            return redirect('verify_otp', username=user.username)
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})


def verify_otp(request, username):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if username in otp_storage and otp_storage[username] == entered_otp:
            # Activate the user and login
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()

            # Log the user in
            auth_login(request, user)

            # Remove OTP from storage
            del otp_storage[username]

            return redirect('home')  # Redirect to the home page

        # Invalid OTP
        return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')




def login(request):  # Your custom login view
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Use the aliased Django login
            return redirect('home')  # Replace 'home' with your home URL name
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

    

@login_required
def profile_up(request):
    try:
        profile = profile1.objects.get(user=request.user)
    except profile1.DoesNotExist:
        profile = profile1(user=request.user)  # Create if not exists

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after saving
    else:
        form = ProfileForm(instance=profile)  # Pre-fill form with current profile data

    return render(request, 'profile_up.html', {'form': form})

@login_required
def chat(request, user_id):
    # Get the recipient user object
    recipient = get_object_or_404(User, id=user_id)

    # Get all messages between the current user and the recipient
    messages = ChatMessage.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=recipient)) |
        (models.Q(sender=recipient) & models.Q(receiver=request.user))
    ).order_by('timestamp')

    return render(request, 'chat.html', {
        'recipient': recipient,
        'messages': messages,
    })
@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get('content', '')
        receiver_id = request.POST.get('receiver_id')
        file = request.FILES.get('file')

        receiver = get_object_or_404(User, id=receiver_id)

        message = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            file=file,  # Make sure this is saved correctly
        )

        response_data = {
            'message': {
                'content': message.content,
                'sender_id': message.sender.id,
                'file_url': message.file.url if message.file else None,
            }
        }

        return JsonResponse(response_data)



from django.db.models import Q

@login_required
def get_messages(request, recipient_id):
    if request.method == 'GET':
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver_id=recipient_id) |
            Q(sender_id=recipient_id, receiver=request.user)
        ).order_by('timestamp').values('sender_id', 'receiver_id', 'content', 'timestamp', 'file')

        # Prepare the data to include file_url
        messages_data = []
        for message in messages:
            message_data = {
                'sender_id': message['sender_id'],
                'receiver_id': message['receiver_id'],
                'content': message['content'],
                'timestamp': message['timestamp'],
                'file_url': message['file'] if message['file'] else None,  # Use the file path directly
            }
            messages_data.append(message_data)

        return JsonResponse({'messages': messages_data})
    return JsonResponse({'error': 'Invalid request method'}, status=405)







@login_required
def chat_view(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    messages = ChatMessage.objects.filter(
        sender=request.user, receiver=recipient
    ) | ChatMessage.objects.filter(
        sender=recipient, receiver=request.user
    ).order_by('timestamp')

    context = {
        'recipient': recipient,
        'messages': messages,
    }
    return render(request, 'chat.html', context)



@login_required
def user_list_view(request):
    
    current_user = request.user
    # Get distinct users with whom the current user has chatted
    sent_messages = ChatMessage.objects.filter(sender=current_user).select_related('receiver')
    received_messages = ChatMessage.objects.filter(receiver=current_user).select_related('sender')

    # Combine unique users from both sent and received messages
    users = set(
        [msg.receiver for msg in sent_messages] + 
        [msg.sender for msg in received_messages if msg.sender != current_user]
    )

    user_data = []
    for user in users:
        profile = getattr(user, 'profile1', None)  # Get profile1 object if it exists
        user_data.append({
            "id": user.id,
            "username": user.username,
            "last_message": ChatMessage.objects.filter(
                sender=current_user, receiver=user
            ).order_by('-timestamp').first() or ChatMessage.objects.filter(
                sender=user, receiver=current_user
            ).order_by('-timestamp').first(),
            "profile_image": profile.photo1.url if profile and profile.photo1 else "/static/default-profile.png",
        })

    return render(request, "user_list.html", {"users": user_data})

@login_required
def an_profile_view(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        profile = profile1.objects.get(user=user)
    except profile1.DoesNotExist:
        return render(request, 'profile.html', {'user': user})
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'profile.html', context)




def search_profiles(request):
    query = request.GET.get('q', '')  # Get the search query from the URL
    if query:
        results = profile1.objects.filter(
            Q(name__icontains=query) |
            Q(photo1__icontains=query) |
            Q(photo2__icontains=query) |
            Q(photo3__icontains=query) |
            Q(interest1__icontains=query) |
            Q(interest2__icontains=query) |
            Q(interest3__icontains=query) |
            Q(interest4__icontains=query) |
            Q(interest5__icontains=query)
        )
    else:
        results = profile1.objects.none()  # Return an empty QuerySet if no query
    return render(request, 'search.html', {'profiles': results, 'query': query})