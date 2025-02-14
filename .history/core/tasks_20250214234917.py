from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ActionableStep


@shared_task
def send_reminder(step_id):
    try:
        step = ActionableStep.objects.get(id=step_id, active=True)
        # Log or send the reminder (for demonstration, we print it)
        print(f"Reminder: {step.description}")

        # If the patient hasn't checked in, schedule another reminder for 1 day later.
        if not step.checked_in:
            next_scheduled_time = timezone.now() + timedelta(days=1)
            # Optionally update the scheduled time in the model (if you want to track it)
            step.scheduled_time = next_scheduled_time
            step.save()
            # Schedule the reminder again
            send_reminder.apply_async((step.id,), eta=next_scheduled_time)
    except ActionableStep.DoesNotExist:
        pass


def schedule_reminders(step):
    # Schedule the reminder task using Celery.
    send_reminder.apply_async((step.id,), eta=step.scheduled_time)


def cancel_previous_steps(patient):
    # Deactivate any previously active actionable steps for the given patient.
    ActionableStep.objects.filter(note__patient=patient, active=True).update(
        active=False
    )
