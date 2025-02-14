from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import DoctorNote, ActionableStep, DoctorPatientAssignment
from .serializers import (
    UserSignupSerializer,
    DoctorNoteSerializer,
    ActionableStepSerializer,
    DoctorPatientAssignmentSerializer,
)
from .tasks import schedule_reminders, cancel_previous_steps
from .llm import process_note_with_llm


User = get_user_model()


def process_note_with_llm(raw_note: str):
    """
    Simulate a live LLM API call to extract actionable steps.
    Replace this simulation with an actual API call.
    """
    checklist = [{"description": "Buy prescribed drug"}]
    plan = [
        {
            "description": "Take drug daily for 7 days",
            "scheduled_time": (timezone.now() + timezone.timedelta(days=1)),
        }
    ]
    return checklist, plan


class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]


class DoctorNoteView(generics.CreateAPIView):
    serializer_class = DoctorNoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # The authenticated user must be the doctor.
        serializer.save(doctor=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        note = DoctorNote.objects.get(id=response.data["id"])
        # Cancel previously scheduled actionable steps for the patient.
        cancel_previous_steps(note.patient)
        # Process the note with the live LLM to extract actionable steps.
        checklist, plan = process_note_with_llm(request.data.get("raw_note"))
        for item in checklist:
            ActionableStep.objects.create(
                note=note, step_type="checklist", description=item["description"]
            )
        for item in plan:
            step = ActionableStep.objects.create(
                note=note,
                step_type="plan",
                description=item["description"],
                scheduled_time=item["scheduled_time"],
            )
            # Schedule reminders using Celery.
            schedule_reminders(step)
        return response


class PatientDoctorAssignmentView(generics.CreateAPIView):
    serializer_class = DoctorPatientAssignmentSerializer
    permission_classes = [IsAuthenticated]


class DoctorPatientsListView(generics.ListAPIView):
    serializer_class = DoctorPatientAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return all patients assigned to the authenticated doctor.
        return DoctorPatientAssignment.objects.filter(doctor=self.request.user)


class ActionableStepsView(generics.ListAPIView):
    serializer_class = ActionableStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return active actionable steps for the authenticated patient.
        return ActionableStep.objects.filter(
            note__patient=self.request.user, active=True
        )


class AvailableDoctorsListView(generics.ListAPIView):
    """
    Lists all available doctors so that patients can choose one.
    """

    permission_classes = [AllowAny]
    serializer_class = (
        UserSignupSerializer  # You might want a custom serializer with limited fields.
    )

    def get_queryset(self):
        return User.objects.filter(is_doctor=True)


class ForgotPasswordView(generics.GenericAPIView):
    """
    Simulate a forgot password endpoint.
    In production, integrate with Django's email system.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
            # In production, you would send an email with a password reset link.
            # For demo purposes, we'll just return a success message.
            return Response({"message": f"Password reset link sent to {email}."})
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CheckInView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, step_id, *args, **kwargs):
        try:
            step = ActionableStep.objects.get(id=step_id, active=True)
            # Mark as checked in
            step.checked_in = True
            step.save()
            return Response(
                {"message": "Check-in successful."}, status=status.HTTP_200_OK
            )
        except ActionableStep.DoesNotExist:
            return Response(
                {"error": "Actionable step not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
