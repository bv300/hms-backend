from django.shortcuts import render
# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Patient
from .models import ProfileIcon
from .serializers import PatientSerializer
from .serializers import ProfileIconSerializer
from .serializers import ProfileSerializer
from .models import Slider
from .serializers import SliderSerializer
from .models import Doctor
from .serializers import DoctorSerializer
from .models import Appointment
from .serializers import AppointmentSerializer
from .models import Medicine, MedicineSale
from .serializers import MedicineSerializer, MedicineSaleSerializer
from .serializers import DepartmentSerializer
from .models import Department
from .models import User, PasswordResetOTP
# from django.core.mail import send_mail
import random
# from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate 
# from .models import Staff_user
from functools import wraps
# from rest_framework.generics import GenegicAPIView

# class API(GenegicAPIView):
#     serializer_class = AllowAny


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required"}, status=401)

            if request.user.role not in allowed_roles and not request.user.is_superuser:
                return Response({"error": "Permission denied"}, status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator





@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def patient_list(request):
    if request.method == 'GET':
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'PUT':
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        patient.delete()
        return Response({"message": "Patient deleted"}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProfileIcony(request):
    icons = ProfileIcon.objects.all()         
    serializer = ProfileIconSerializer(icons, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def slider_api(request):
    sliders = Slider.objects.all()
    serializer = SliderSerializer(sliders, many=True)
    return Response(serializer.data)

from django.shortcuts import get_object_or_404
from .models import Slider
from .serializers import SliderSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def slider_detail_api(request, pk):
    slider = get_object_or_404(Slider, pk=pk)
    serializer = SliderSerializer(slider)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def doctor_list(request):
    if request.method == 'GET':
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from django.shortcuts import get_object_or_404

@api_view(['GET', 'PUT', 'DELETE'])
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, id=pk)

    if request.method == 'DELETE':
        doctor.delete()
        return Response({"message": "Doctor deleted"}, status=204)
    

from django.utils.dateparse import parse_date
from django.db.models import F, Window
from django.db.models.functions import RowNumber

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointment_list(request):

    # ---------- GET (LIST + DATE FILTER) ----------
    if request.method == 'GET':
        appointments = Appointment.objects.select_related(
            "patient",
            "doctor",
            "doctor__department"
        )

        # DATE SEARCH FILTER
        date_str = request.GET.get("date")
        if date_str:
            date = parse_date(date_str)
            if date:
                appointments = appointments.filter(date__date=date)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    # ---------- POST (CREATE) ----------
    if request.method == 'POST':
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            return Response(
                AppointmentSerializer(appointment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def medicine_list(request):
    if request.method == 'GET':
        medicines = Medicine.objects.all()
        return Response(MedicineSerializer(medicines, many=True).data)

    if request.method == 'POST':
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_medicine(request):
    medicine_id = request.data.get("medicine")
    quantity = request.data.get("quantity")

    # Quantity validation
    if not quantity:
        return Response({"error": "Quantity is required"}, status=400)

    try:
        qty = int(quantity)
    except ValueError:
        return Response({"error": "Quantity must be a number"}, status=400)

    if qty < 1:
        return Response({"error": "Quantity must be at least 1"}, status=400)

    if qty > 1000:
        return Response({"error": "Maximum quantity allowed is 1000"}, status=400)

    medicine = Medicine.objects.get(id=medicine_id)

    if medicine.stock < qty:
        return Response({"error": "Insufficient stock"}, status=400)

    total = medicine.price * qty
    medicine.stock -= qty
    medicine.save()

    sale = MedicineSale.objects.create(
        medicine=medicine,
        quantity=qty,
        total_price=total
    )

    return Response(MedicineSaleSerializer(sale).data, status=201)


@api_view(['PUT'])
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    serializer = MedicineSerializer(medicine, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def department_list(request):
    if request.method == 'GET':
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)




from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny


User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    print("REGISTER DATA:", request.data)  
    email = request.data.get("email")
    password = request.data.get("password")
    role = request.data.get("role")
    otp = request.data.get("otp")

    if role == "receptionist":
        return Response({"error": "Receptionist cannot self-register"}, status=403)

    if not email or not password or not role:
        return Response({"error": "All fields required"}, status=400)

    if role in ["doctor", "pharmacy"]:
        record = RegistrationOTP.objects.filter(
            email=email,
            role=role
        ).last()

        if not record or record.is_expired() or record.otp != otp:
            return Response({"error": "Invalid or expired OTP"}, status=400)

        record.delete()  # OTP used once

    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_user(
        email=email,
        password=password,
        role=role
    )

    return Response({
        "message": "Registered successfully",
        "role": user.role
    }, status=201)

        
# @api_view(["POST"])
# def login_view(request):
#     email = request.data.get("email")
#     password = request.data.get("password")

#     user = authenticate(request , email=email, password=password)

#     if user :
#         return Response({
#             "message": "Login successful",
#             "role": user.role   
#         })
#     else:
#         return Response({"error": "Invalid credentials"}, status=401)


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

@api_view(["POST"])
@permission_classes([])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, email=email, password=password)
    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "role": user.role,
        "email": user.email,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }, status=200)

        
        
from django.contrib.auth import logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out"})





from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Doctor, Appointment
from .serializers import AppointmentSerializer, DoctorSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_slots(request, pk):
    """
    Return available time slots for doctor pk on a given date (YYYY-MM-DD).
    Query params:
      - date (required): YYYY-MM-DD
      - interval (optional): minutes per slot (default: 30)
    """
    date_str = request.GET.get("date")
    if not date_str:
        return Response({"detail": "date query param required (YYYY-MM-DD)"},
                        status=status.HTTP_400_BAD_REQUEST)

    date_obj = parse_date(date_str)
    if date_obj is None:
        return Response({"detail": "invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

    doctor = get_object_or_404(Doctor, pk=pk)

    try:
        interval = int(request.GET.get("interval", 30))
    except ValueError:
        interval = 30

    # Build naive datetimes on that date using doctor's available_from/to
    start_dt = datetime.combine(date_obj, doctor.available_from)
    end_dt = datetime.combine(date_obj, doctor.available_to)

    # generate slots that start at start_dt and end before or at end_dt
    current = start_dt
    slots = []
    while current + timedelta(minutes=interval) <= end_dt:
        slots.append(current.time().strftime("%H:%M"))
        current += timedelta(minutes=interval)

    # remove already booked times
    booked_qs = Appointment.objects.filter(doctor=doctor, date__date=date_obj)
    booked = {a.date.time().strftime("%H:%M") for a in booked_qs}

    available_slots = [s for s in slots if s not in booked]

    return Response({"date": date_str, "interval": interval, "slots": available_slots})





from .models import User, RegistrationOTP, SystemSettings
from .utils import generate_otp, send_otp_email
from .models import SystemSettings
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def request_staff_otp(request):
    email = request.data.get("email")
    role = request.data.get("role")

    if role not in ["doctor", "pharmacy"]:
        return Response({"error": "OTP not required"}, status=400)

    settings = SystemSettings.objects.first()
    if not settings:
        return Response({"error": "Receptionist email not configured"}, status=500)

    otp = generate_otp()

    RegistrationOTP.objects.create(
        email=email,
        role=role,
        otp=otp
    )

    send_otp_email(settings.default_receptionist_email, otp)

    return Response({"message": "OTP sent to receptionist"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_list(request):
    sales = MedicineSale.objects.all().order_by('-date')
    serializer = MedicineSaleSerializer(sales, many=True)
    return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        serializer = ProfileSerializer(
            request.user,
            context={"request": request}
        )
        return Response(serializer.data)

    def patch(self, request):
        user = request.user

        # IMAGE
        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]

        # OTHER FIELDS
        user.full_name = request.data.get("full_name", user.full_name)
        user.phone = request.data.get("phone", user.phone)
        user.age = request.data.get("age", user.age)
        user.address = request.data.get("address", user.address)
        user.place = request.data.get("place", user.place)

        user.save()

        serializer = ProfileSerializer(
            user,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])   #  IMPORTANT
def forgot_password(request):
    email = request.data.get("email")

    if not User.objects.filter(email=email).exists():
        return Response({"error": "User not found"}, status=404)

    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(email=email, otp=otp)

    # SEND OTP VIA EMAIL HERE
    print("PASSWORD RESET OTP:", otp)

    return Response({"message": "OTP sent"})


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    password = request.data.get("password")

    record = PasswordResetOTP.objects.filter(email=email).last()

    if not record or record.is_expired() or record.otp != otp:
        return Response({"error": "Invalid OTP"}, status=400)

    user = User.objects.get(email=email)
    user.set_password(password)
    user.save()
    record.delete()

    return Response({"message": "Password reset successful"})


def patch(self, request):
    serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={"request": request}
    )


def get(self, request):
    serializer = ProfileSerializer(
        request.user,
        context={"request": request}
    )
    return Response(serializer.data)
