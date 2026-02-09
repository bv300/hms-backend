from django.urls import path
from . import views
from .views import slider_api
from .views import doctor_list, doctor_detail
from .views import patient_list, patient_detail
from .views import appointment_list
from .views import medicine_list, sell_medicine, medicine_detail
from .views import department_list
# from .views import send_otp, verify_otp ,register_user
from .views import login_view , register_user , request_staff_otp
from .views import billing_list
from .views import forgot_password, reset_password, ProfileView

urlpatterns = [
    path('patients/', patient_list),
    path('patients/<int:pk>/', patient_detail),
    path("api/ProfileIcon/", views.ProfileIcony),
    path('api/slider/', slider_api, name='slider_api'),
    path('api/slider/<int:pk>/', views.slider_detail_api, name='slider_detail_api'),
    path('doctors/', doctor_list, name='doctor-list'),
    path('doctors/<int:pk>/', doctor_detail, name='doctor_detail'),
    path("appointments/", appointment_list),
    path("medicines/", medicine_list),
    path("medicines/sale/", sell_medicine),
    path("medicines/<int:pk>/", medicine_detail),
    path("departments/", department_list),
    # path("send-otp/", send_otp),
    # path("verify-otp/", verify_otp),
    path("api/register_user/", register_user, name="register_user"),
    path("api/login/", login_view),
    path("api/logout/", views.logout_view),
    path("doctors/<int:pk>/slots/", views.doctor_slots, name="doctor-slots"),
    path("api/request_staff_otp/", request_staff_otp),
    path("billing/", billing_list), 
    path("api/profile/", ProfileView.as_view()),
    path("api/forgot_password/", forgot_password),
    path("api/reset_password/", reset_password),
]




