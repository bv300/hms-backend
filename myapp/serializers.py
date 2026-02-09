from rest_framework import serializers
from .models import Patient
from .models import ProfileIcon
from .models import Slider
from .models import Doctor
from .models import Appointment
from .models import Department


        
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model =Patient
        fields='__all__'
        
    def validate_age(self, value):
        if value < 1:
            raise serializers.ValidationError("Age must be greater than 0")
        return value

    def create(self, validated_data):
        # case-insensitive existing check by name
        name = validated_data.get("name", "").strip()
        if not name:
            raise serializers.ValidationError({"name": "Name is required."})

        # try find existing by case-insensitive name
        patient = Patient.objects.filter(name__iexact=name).first()
        if patient:
            # if found, optionally update missing fields from validated_data:
            # for simplicity return existing patient unchanged
            return patient

        # otherwise, create new patient (missing fields are allowed)
        validated_data["name"] = name
        return Patient.objects.create(**validated_data)
    
        
class ProfileIconSerializer(serializers.ModelSerializer):
    class Meta :
        model = ProfileIcon
        fields='__all__'
        



class SliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Slider
        fields = ['id', 'title', 'description', 'image']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ""
    

class DoctorSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = "__all__"

    def validate_experience(self, value):
        if value < 1:
            raise serializers.ValidationError("Experience must be greater than 0")
        return value











class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    department_name = serializers.CharField(
        source="doctor.department.name",
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = "__all__"
        
    def validate(self, data):
        doctor = data["doctor"]
        dt = data["date"]
        t = dt.time()

        if t < doctor.available_from or t >= doctor.available_to:
            raise serializers.ValidationError(
                f"Doctor available from {doctor.available_from} to {doctor.available_to}"
            )

        if Appointment.objects.filter(doctor=doctor, date=dt).exists():
            raise serializers.ValidationError("This slot is already booked")

        return data
        
from rest_framework import serializers
from .models import Medicine, MedicineSale

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = "__all__"
    def validate(self, data):
        mfgs = data.get("manufacturing_date")
        exp = data.get("expiry_date")

        if mfgs and exp and exp <= mfgs:
            raise serializers.ValidationError(
                 "Expiry date must be after manufacturing date"
        )
        return data



class MedicineSaleSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)

    class Meta:
        model = MedicineSale
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


from rest_framework import serializers
from .models import User

class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields =  [
            "id",
            "email",
            "role",
            "profile_image",
            "full_name",
            "phone",
            "age",
            "address",
            "place",
        ]
        
    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
