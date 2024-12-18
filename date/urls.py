from django.urls import path 
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
urlpatterns = [
     path('', views.signup, name='signup'),
     path('login', views.login, name='login'),
     path('home/', views.home, name='home'),
     path('notifications/redirect/<int:notification_id>/', views.redirect_to_chat_from_notification, name='redirect_to_chat_from_notification'),  
     path('notifications/', views.notifications, name='notifications'),
     path('profile/', views.profile, name='profile'),
     path('profile_up/', views.profile_up, name='profile_up'),
     path('notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_as_read'),
     path('chat/<int:user_id>/', views.chat, name='chat'),
     path('chat/send/', views.send_message, name='send_message'),
     path('chat/messages/<int:recipient_id>/', views.get_messages, name='get_messages'),
     path('messages/<int:user_id>/', views.chat_view, name='chat_view'),  # This is the required pattern
     path('user-list/', views.user_list_view, name='user_list_view'),    # Add other p
     path('an_profile_view/<int:user_id>/', views.an_profile_view, name='an_profile_view'),
     path('search/', views.search_profiles, name='search_profiles'),
     path('verify-otp/<str:username>/', views.verify_otp, name='verify_otp'),
    


     path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
     path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
]

    

    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
