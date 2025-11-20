import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager

class User(AbstractBaseUser):
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Primary login field
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True) 
    full_name = models.CharField(max_length=150, blank=True)
    
    # Role choices
    class Role(models.TextChoices):
        STAFF = "staff", "Staff"
        APPROVER_L1 = "approver-level-1", "Approver Level 1"
        APPROVER_L2 = "approver-level-2", "Approver Level 2"
        FINANCE = "finance", "Finance"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF
    )

    # CRITICAL: Login is based on email
    USERNAME_FIELD = 'email' 
    
    # Only prompting for full_name when creating superuser
    REQUIRED_FIELDS = ['full_name'] 
    
    objects = UserManager() 

    def __str__(self):
        return self.email