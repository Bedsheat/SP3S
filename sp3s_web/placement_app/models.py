from django.db import models
from django.contrib.auth.models import User

BRANCH_CHOICES = [
    ('COMP', 'Computer Engineering (COMP)'),
    ('CSE', 'Computer Science & Engineering (CSE)'),
    ('EXTC', 'Electronics & Telecommunication (EXTC)'),
    ('MCA', 'Master of Computer Applications (MCA)'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, default='CSE')
    stipend = models.FloatField(default=0.0, help_text="Monthly Internship Stipend in INR")
    tenth_percentage = models.FloatField(default=85.0, help_text="10th Class Percentage (0-100)")
    twelfth_percentage = models.FloatField(default=85.0, help_text="12th Class Percentage (0-100)")
    cgpa = models.FloatField(default=8.0, help_text="Engineering/Degree CGPA (0-10)")
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.branch}, CGPA: {self.cgpa})"
