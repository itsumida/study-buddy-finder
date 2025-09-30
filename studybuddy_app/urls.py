# studybuddy_app/urls.py (App URLs)
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'studybuddy_app'

urlpatterns = [
    # ===========================================
    # MAIN PAGES
    # ===========================================
    path('', views.index, name='index'),
    path('about/', views.more_about, name='about'),
   
    
    # ===========================================
    # AUTHENTICATION
    # ===========================================
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # ===========================================
    # PROFILE MANAGEMENT
    # ===========================================
    path('profile/add/', login_required(views.profile_add), name='profile_add'),
    path('profile/edit/', login_required(views.edit_my_profile), name='edit_my_profile'),  #Edit current user's profile
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile/<int:pk>/edit/', login_required(views.profile_edit), name='profile_edit'),
    path('profiles/', login_required(views.profile_list), name='profile_list'),
    path('user-profile/<int:pk>/', views.user_profile, name='user_profile'),
    
    # ===========================================
    # STUDY BUDDY MATCHING
    # ===========================================
    path('find-buddies/', login_required(views.find_buddies), name='find_buddies'),
    
    # ===========================================
    # MESSAGING SYSTEM
    # ===========================================
    path('inbox/', login_required(views.inbox), name='inbox'),
    path('send-message/<int:receiver_id>/', login_required(views.send_message), name='send_message'),
    path('chat/<int:user_id>/', login_required(views.chat_thread), name='chat_thread'),
    path('reply/<int:sender_id>/', login_required(views.reply_message), name='reply_message'),
    
    # ===========================================
    # REVIEW SYSTEM
    # ===========================================
    path('review/<int:profile_id>/', login_required(views.leave_review), name='leave_review'),
    path('reviews/', views.reviews_list, name='reviews_list'),  # Reviews list page
]