from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.core.paginator import Paginator


from .forms import (
    ProfileAddForm, ReviewForm, ProfileEditForm, MessageForm, CustomUserCreationForm
)
from .models import (
    Profile, Message, Review, Match
)


def create_matches_for_profile(profile):
    """Create matches for a profile based on shared courses"""
    others = Profile.objects.exclude(id=profile.id)

    for other in others:
        shared_courses = profile.courses.filter(id__in=other.courses.values_list("id", flat=True))
        for course in shared_courses:
            # Ensure order is consistent (profile1.id < profile2.id)
            profile1, profile2 = sorted([profile, other], key=lambda p: p.id)

            Match.objects.get_or_create(
                profile1=profile1,
                profile2=profile2,
                course=course
            )


# ---------------------------------------
# Main Views
# ---------------------------------------
def index(request):
    """Homepage view"""
    try:
        featured_profiles = None
        has_unread = False

        if request.user.is_authenticated:
            featured_profiles = Profile.objects.exclude(user=request.user).order_by('?')[:3]
            has_unread = Message.objects.filter(receiver=request.user, read=False).exists()

        return render(request, 'studybuddy_app/index.html', {
            'featured_profiles': featured_profiles,
            'has_unread': has_unread
        })

    except Exception as e:
        messages.error(request, "An error occurred while loading the homepage.")
        return render(request, 'studybuddy_app/index.html', {
            'has_unread': False
        })

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
import re


def signup(request):
    if request.user.is_authenticated:
        return redirect('studybuddy_app:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        elif not re.match(r"^s\d{7}@bi\.no$", email):
            messages.error(request, "Email must be in the format s1234567@bi.no.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            Profile.objects.create(user=user, email=email)  # if Profile model has `email` field
            messages.success(request, f"Welcome, {username}!")
            return redirect('studybuddy_app:profile_add')  # guide user to complete profile

    return render(request, 'studybuddy_app/signup.html')


from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
    if request.user.is_authenticated:
        return redirect('studybuddy_app:index')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        try:
            profile = user.profile
            return redirect('studybuddy_app:profile', pk=profile.pk)
        except Profile.DoesNotExist:
            messages.info(request, "Please complete your profile.")
            return redirect('studybuddy_app:profile_add')

    elif request.method == 'POST':
        messages.error(request, "Invalid username or password.")

    return render(request, 'studybuddy_app/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f"Goodbye {username}! You have been logged out.")
    return redirect('studybuddy_app:index')


def more_about(request):
    """About page view"""
    return render(request, 'studybuddy_app/profile/more_about.html')


# ---------------------------------------
# Profile Views
# ---------------------------------------
def profile(request, pk):
    """Display user profile"""
    try:
        profile = get_object_or_404(Profile, pk=pk)
        

        
        reviews = Review.objects.filter(reviewed_user=profile.user).select_related('reviewer')
        can_review = (
            request.user.is_authenticated and
            request.user != profile.user and 
            not Review.objects.filter(reviewer=request.user, reviewed_user=profile.user).exists()
        )

        return render(request, 'studybuddy_app/profile/profile.html', {
            'profile': profile,
            'reviews': reviews,
            'can_review': can_review
        })
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return redirect('studybuddy_app:index')


@login_required
def profile_list(request):
    """List all user profiles with pagination"""
    try:
        profiles = Profile.objects.exclude(user=request.user).select_related('user')
        paginator = Paginator(profiles, 10)  # Show 10 profiles per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'studybuddy_app/profile/profile_list.html', {'page_obj': page_obj})
    except Exception as e:
        messages.error(request, f"Error loading profiles: {e}")
        return render(request, 'studybuddy_app/profile/profile_list.html', {'page_obj': None})


@login_required

def profile_add(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileAddForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            form.save_m2m()
            create_matches_for_profile(profile)
            messages.success(request, "Profile saved successfully!")
            return redirect('studybuddy_app:profile', pk=profile.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileAddForm(instance=profile)

    return render(request, 'studybuddy_app/profile/profile_add.html', {'form': form})



@login_required
def edit_my_profile(request):
    """Redirect to edit the current user's own profile"""
    try:
        profile = request.user.profile
        return redirect('studybuddy_app:profile_edit', pk=profile.pk)
    except:
        # If user doesn't have a profile yet, redirecting to create one
        return redirect('studybuddy_app:profile_add')


@login_required
def profile_edit(request, pk):
    """Edit user profile"""
    profile = get_object_or_404(Profile, pk=pk)

    # Checking if the logged-in user matches the profile user
    if request.user != profile.user:
        messages.error(request, "You are not authorized to edit this profile.")
        return redirect('studybuddy_app:profile', pk=profile.pk)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                form.save_m2m()
                create_matches_for_profile(profile)
                messages.success(request, "Profile updated successfully!")
                return redirect('studybuddy_app:profile', pk=profile.pk)
            except Exception as e:
                messages.error(request, f"Error saving profile: {str(e)}")
        else:
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'studybuddy_app/profile/profile_edit.html', {'form': form, 'profile': profile})


def user_profile(request, pk):
    """View another user's profile and send message"""
    target_profile = get_object_or_404(Profile, pk=pk)
    message_sent = False

    if request.method == 'POST' and request.user.is_authenticated:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = target_profile.user
            message.save()
            message_sent = True
            messages.success(request, "Message sent successfully!")
            form = MessageForm()  # Clear form after submission
        else:
            messages.error(request, "Error sending message.")
    else:
        form = MessageForm()

    return render(request, 'studybuddy_app/profile/profile_user_info.html', {
        'profile': target_profile,
        'form': form,
        'message_sent': message_sent
    })


@login_required
def find_buddies(request):
    """Find study buddies based on matches"""
    try:
        profile = request.user.profile
        matches = Match.objects.filter(Q(profile1=profile) | Q(profile2=profile))

        matched_profiles = {}
        for match in matches:
            other = match.profile2 if match.profile1 == profile else match.profile1
            matched_profiles.setdefault(other, []).append(match.course)

        return render(request, 'studybuddy_app/profile/find_buddies.html', {
            'matched_profiles': matched_profiles
        })
    except ObjectDoesNotExist:
        messages.error(request, "Please create a profile first to find study buddies.")
        return redirect('studybuddy_app:profile_add')
    except Exception as e:
        messages.error(request, f"Error finding buddies: {str(e)}")
        return redirect('studybuddy_app:index')


# ---------------------------------------
# Messaging System
# ---------------------------------------
@login_required
def send_message(request, receiver_id):
    """Send a message to another user"""
    receiver = get_object_or_404(User, id=receiver_id)

    # Prevent sending message to yourself
    if receiver == request.user:
        messages.error(request, "You cannot send a message to yourself.")
        return redirect('studybuddy_app:inbox')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            try:
                Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=content
                )
                messages.success(request, "Message sent successfully!")
                return redirect('studybuddy_app:chat_thread', user_id=receiver.id)
            except Exception as e:
                messages.error(request, "Error sending message.")
        else:
            messages.error(request, "Message cannot be empty.")
    
    return render(request, 'studybuddy_app/messages/send_message.html', {'receiver': receiver})


@login_required
def inbox(request):
    """Display user's message inbox"""
    user = request.user

    # Mark all unread messages as read
    Message.objects.filter(receiver=user, read=False).update(read=True)

    all_messages = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).exclude(sender=user, receiver=user).order_by('-created_at')

    threads = {}
    for msg in all_messages:
        other_user = msg.receiver if msg.sender == user else msg.sender
        if other_user.id not in threads:
            threads[other_user.id] = {
                'user': other_user,
                'last_message': msg
            }

    return render(request, 'studybuddy_app/messages/inbox.html', {
        'threads': threads.values()
    })


@login_required
def chat_thread(request, user_id):
    """Display chat thread with another user"""
    if user_id == request.user.id:
        messages.error(request, "You cannot chat with yourself.")
        return redirect('studybuddy_app:inbox')

    partner = get_object_or_404(User, id=user_id)

    messages_received = Message.objects.filter(
        Q(sender=request.user, receiver=partner) |
        Q(sender=partner, receiver=request.user)
    ).exclude(sender=request.user, receiver=request.user).order_by('created_at')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            try:
                Message.objects.create(
                    sender=request.user,
                    receiver=partner,
                    content=content
                )
                return redirect('studybuddy_app:chat_thread', user_id=partner.id)
            except Exception as e:
                messages.error(request, "Error sending message.")

    return render(request, 'studybuddy_app/messages/chat_thread.html', {
        'messages_received': messages_received,
        'receiver': partner,
    })


@login_required
def reply_message(request, sender_id):
    """Reply to a specific message"""
    original_message = get_object_or_404(Message, id=sender_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.receiver = original_message.sender
            reply.replied_to = original_message
            reply.save()
            messages.success(request, "Reply sent successfully!")
            return redirect('studybuddy_app:inbox')
        else:
            messages.error(request, "Error sending reply.")
    else:
        form = MessageForm()

    return render(request, 'studybuddy_app/messages/reply.html', {
        'form': form,
        'original_message': original_message,
    })


# ---------------------------------------
# Review System
# ---------------------------------------
@login_required
def leave_review(request, profile_id):
    """Leave a review for another user"""
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.user == profile.user:
        messages.error(request, "You cannot review yourself.")
        return redirect('studybuddy_app:profile', pk=profile_id)
        
    if Review.objects.filter(reviewer=request.user, reviewed_user=profile.user).exists():
        messages.error(request, "You have already reviewed this user.")
        return redirect('studybuddy_app:profile', pk=profile_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        print("Form errors:", form.errors)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.reviewer = request.user
                review.reviewed_user = profile.user
                review.save()
                messages.success(request, "Review submitted successfully!")
                return redirect('studybuddy_app:profile', pk=profile_id)
            except Exception as e:
                messages.error(request, "Error submitting review.")
        else:
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReviewForm()
    
    return render(request, 'studybuddy_app/leave_review.html', {
        'form': form,
        'profile': profile
    })


def reviews_list(request):
    """Display all reviews with filtering and pagination"""
    try:
        # Get filter parameters
        rating_filter = request.GET.get('rating', '')
        sort_by = request.GET.get('sort', 'newest')
        
        # Start with all reviews
        reviews = Review.objects.select_related('reviewer', 'reviewed_user').all()
        
        # Apply rating filter
        if rating_filter and rating_filter.isdigit():
            rating_value = int(rating_filter)
            reviews = reviews.filter(rating__gte=rating_value)
        
        # Apply sorting
        if sort_by == 'newest':
            reviews = reviews.order_by('-created_at')
        elif sort_by == 'oldest':
            reviews = reviews.order_by('created_at')
        elif sort_by == 'highest':
            reviews = reviews.order_by('-rating', '-created_at')
        elif sort_by == 'lowest':
            reviews = reviews.order_by('rating', '-created_at')
        else:
            reviews = reviews.order_by('-created_at')
        
        # Calculate statistics
        stats = Review.objects.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            five_star_count=Count('id', filter=Q(rating=5)),
            active_reviewers=Count('reviewer', distinct=True)
        )
        
        # Handle None values
        total_reviews = stats['total_reviews'] or 0
        average_rating = stats['average_rating'] or 0
        five_star_reviews = stats['five_star_count'] or 0
        active_reviewers = stats['active_reviewers'] or 0
        
        # Pagination
        paginator = Paginator(reviews, 12)  # Show 12 reviews per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'studybuddy_app/reviews_list.html', {
            'page_obj': page_obj,
            'total_reviews': total_reviews,
            'average_rating': average_rating,
            'five_star_reviews': five_star_reviews,
            'active_reviewers': active_reviewers,
        })
        
    except Exception as e:
        messages.error(request, "Error loading reviews.")
        return render(request, 'studybuddy_app/reviews_list.html', {
            'page_obj': None,
            'total_reviews': 0,
            'average_rating': 0,
            'five_star_reviews': 0,
            'active_reviewers': 0,
        })



# ---------------------------------------
# Search Functionality
# ---------------------------------------
def search_buddies(request):
    """Search for study buddies based on various criteria"""
    query = request.GET.get('q', '').strip()
    
    try:
        if query:
            results = Profile.objects.filter(
                Q(courses__name__icontains=query) |
                Q(study_methods__icontains=query) |
                Q(bio__icontains=query) |
                Q(user__username__icontains=query)
            ).exclude(user=request.user if request.user.is_authenticated else None).distinct()
            
            paginator = Paginator(results, 10)  # Show 10 results per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = None
            messages.info(request, "Please enter a search term.")
        
        return render(request, 'studybuddy_app/search_results.html', {
            'page_obj': page_obj,
            'query': query
        })
    except Exception as e:
        messages.error(request, "Error performing search.")
        return render(request, 'studybuddy_app/search_results.html', {
            'page_obj': None, 
            'query': query
        })
