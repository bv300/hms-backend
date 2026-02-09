from django.db import models
from django.contrib.auth.models import AbstractUser


class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="patients/", null=True, blank=True)
    
    
    @property
    def is_incomplete(self):
        return not (self.age and self.phone and self.address)
    
    def __str__(self):
        return self.name


class ProfileIcon(models.Model):
    image = models.ImageField(upload_to='profile')


class Slider(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='slider/', null=True, blank=True)
    
    def __str__(self):
        return self.title


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        'myapp.Department',
        on_delete=models.CASCADE,
        related_name="doctors"
    )
    specialization = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    degree = models.CharField(max_length=50, blank=True, null=True)
    experience = models.IntegerField(default=0)
    image = models.ImageField(upload_to="doctors/", null=True, blank=True)
    qualification = models.CharField(max_length=255)
    available_from = models.TimeField(default='09:00:00')
    available_to = models.TimeField(default='17:00:00')


    def __str__(self):
        return self.name

from django.db.models import Max

class Appointment(models.Model):
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        "Doctor",
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    date = models.DateTimeField()
    token = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            last_token = Appointment.objects.filter(
                doctor=self.doctor,
                date__date=self.date.date()
            ).aggregate(Max("token"))["token__max"]

            self.token = (last_token or 0) + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.date})"


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, null=True, blank=True)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)
    mfg_date=models.DateField(null=True,blank=True)

    def __str__(self):
        return self.name


class MedicineSale(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="sales")
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity}"


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name






from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email=None, password=None, **extra_fields):
        # Accept and ignore `username` kwarg (some callers pass username=email)
        username = extra_fields.pop("username", None)

        # If email wasn't provided but username was used for email, use it
        if not email and username:
            email = username

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # Allow callers that may pass `username` kwarg
        return self.create_user(email=email, password=password, **extra_fields)
    
    
class User(AbstractUser):
        username = None
        email = models.EmailField(unique=True)
        ROLE_CHOICES = (
            ("doctor", "Doctor"),
            ("receptionist", "Receptionist"),
            ("pharmacy", "Pharmacy"),
            ("patient", "Patient"),
            )
        role = models.CharField(max_length=20, choices=ROLE_CHOICES)
        profile_image = models.ImageField(upload_to="profile/", null=True, blank=True)
        
        full_name = models.CharField(max_length=100, blank=True)
        phone = models.CharField(max_length=15, blank=True)
        age = models.PositiveIntegerField(null=True, blank=True)
        address = models.TextField(blank=True)
        place = models.CharField(max_length=100, blank=True)
        
        USERNAME_FIELD = "email"
        REQUIRED_FIELDS = []
        
        objects = UserManager()  


class SystemSettings(models.Model):
    default_receptionist_email = models.EmailField()


class RegistrationOTP(models.Model):
    email = models.EmailField()
    role = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    
class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
