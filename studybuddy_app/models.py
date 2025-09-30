from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class TimestampModel(models.Model):
    """Abstract base model with created_at and updated_at fields"""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

# -- COURSE --
class Course(TimestampModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

#--PROFILE--
class Profile(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fname = models.CharField("First name", max_length=50)
    lname = models.CharField("Last name", max_length=50)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True) 
    courses = models.ManyToManyField(Course, blank=True, related_name='students')
    study_methods = models.CharField(max_length=200, blank=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['lname', 'fname']

    def __str__(self):
        return f"{self.fname} {self.lname}"

    def full_name(self):
        return f"{self.fname} {self.lname}"

#--STUDY MATCH--
class Match(TimestampModel):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='matches_as_first')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='matches_as_second')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile1', 'profile2', 'course')

    def __str__(self):
        return f"{self.profile1.full_name()} & {self.profile2.full_name()} — {self.course.code}"

#--MESSAGE--
    
class Message(models.Model):
    content = models.TextField()
    read = models.BooleanField(default=False)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    replied_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"

#--REVIEW--
class Review(TimestampModel):
    reviewer = models.ForeignKey(
        User, 
        related_name='given_reviews', 
        on_delete=models.CASCADE
    )
    reviewed_user = models.ForeignKey(
        User, 
        related_name='received_reviews', 
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = [['reviewer', 'reviewed_user']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.username} → {self.reviewed_user.username} ({self.rating}/5)"

