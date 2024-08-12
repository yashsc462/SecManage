from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPES = (
        ('hod', 'HOD'),
        ('fo', 'Field Officer'),
        ('company', 'Company'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='fo')
    contact = models.CharField(max_length=12)
    gst_or_emergency = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.email} ({self.get_user_type_display()})"
