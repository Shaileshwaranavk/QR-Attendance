from rest_framework import serializers
from .models import User, Teacher, Student, Subject, Session, Attendance


# 🔹 User Serializer (no password hashing)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'linked_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # ✅ Store password directly (plain text)
        user = User(
            username=validated_data['username'],
            role=validated_data.get('role'),
            linked_id=validated_data.get('linked_id'),
            password=validated_data['password']
        )
        user.save()
        return user


# 🔹 Teacher Serializer
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'name', 'department', 'email']


# 🔹 Student Serializer
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'department', 'email']


# 🔹 Subject Serializer
class SubjectSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    teacher_id = serializers.CharField(write_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'teacher', 'teacher_id']


# 🔹 Session Serializer
class SessionSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Session
        fields = [
            'id',
            'subject',
            'subject_id',
            'topic',
            'class_date',
            'start_time',
            'end_time'
        ]


# 🔹 Attendance Serializer
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'subject', 'session', 'status', 'marked_at']


# 🔹 Attendance Percentage Serializer
class AttendancePercentageSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    subject_code = serializers.CharField()
    total_classes = serializers.IntegerField()
    attended = serializers.IntegerField()
    percentage = serializers.FloatField()
