from django.urls import path
from .views import (
    UserSignupView,
    DoctorNoteView,
    PatientDoctorAssignmentView,
    DoctorPatientsListView,
    ActionableStepsView,
    AvailableDoctorsListView,
    ForgotPasswordView,
    CheckInView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="user-signup"),
    path("notes/", DoctorNoteView.as_view(), name="doctor-note"),
    path("assign/", PatientDoctorAssignmentView.as_view(), name="doctor-assign"),
    path("my-patients/", DoctorPatientsListView.as_view(), name="doctor-patients"),
    path("steps/", ActionableStepsView.as_view(), name="actionable-steps"),
    path("doctors/", AvailableDoctorsListView.as_view(), name="available-doctors"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path('check-in/<int:step_id>/', CheckInView.as_view(), name='check-in'),
]
