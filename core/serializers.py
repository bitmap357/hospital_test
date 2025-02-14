from rest_framework import serializers
from .models import User, DoctorNote, ActionableStep, DoctorPatientAssignment


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "is_doctor", "is_patient"]

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class DoctorNoteSerializer(serializers.ModelSerializer):
    raw_note = serializers.CharField(write_only=True)
    note_content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DoctorNote
        fields = ["id", "doctor", "patient", "raw_note", "note_content", "created_at"]
        read_only_fields = ["id", "created_at", "note_content"]

    def get_note_content(self, obj):
        request = self.context.get("request")
        if request and (request.user == obj.doctor or request.user == obj.patient):
            return obj.get_note_content()
        return "Unauthorized"

    def create(self, validated_data):
        raw_note = validated_data.pop("raw_note")
        note = DoctorNote(**validated_data)
        note.set_note_content(raw_note)
        note.save()
        return note


class ActionableStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionableStep
        fields = "__all__"


class DoctorPatientAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorPatientAssignment
        fields = "__all__"
