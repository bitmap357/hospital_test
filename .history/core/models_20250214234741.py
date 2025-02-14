import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cryptography.fernet import Fernet

# Retrieve the encryption key from the environment.
# The key must be a url-safe base64-encoded 32-byte key.
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # For development only. In production, set the ENCRYPTION_KEY in .env.
    ENCRYPTION_KEY = Fernet.generate_key().decode()

fernet = Fernet(ENCRYPTION_KEY.encode())


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class DoctorPatientAssignment(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patients"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctors"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} assigned to {self.doctor}"


class DoctorNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes_received",
    )
    # The note is stored in an encrypted binary field.
    encrypted_note = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    def set_note_content(self, raw_text: str):
        self.encrypted_note = fernet.encrypt(raw_text.encode())

    def get_note_content(self) -> str:
        return fernet.decrypt(self.encrypted_note).decode()

    def __str__(self):
        return f"Note by {self.doctor} for {self.patient} at {self.created_at}"


class ActionableStep(models.Model):
    STEP_TYPES = (
        ("checklist", "Checklist"),
        ("plan", "Plan"),
    )
    note = models.ForeignKey(
        DoctorNote, on_delete=models.CASCADE, related_name="actionable_steps"
    )
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    description = models.TextField()
    scheduled_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    checked_in = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"{self.step_type} - {self.description}"
