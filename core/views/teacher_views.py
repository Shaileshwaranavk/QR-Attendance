from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Count, Q, F
from core.models import Subject, Session, Attendance, Student, User
from core.serializers import (
    SubjectSerializer,
    SessionSerializer,
    AttendanceSerializer,
    AttendancePercentageSerializer
)
from core.utils.qr_generator import generate_session_qr
from core.permissions import IsTeacherUserCustom

from rest_framework.permissions import IsAuthenticated, AllowAny

# ✅ Teacher Login (Plaintext Password Version)
class TeacherLoginAPIView(APIView):
    """
    Teacher login — verifies teacher credentials and returns a JWT access token.
    """
    
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required."}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password."}, status=401)

        # ✅ Ensure user is a teacher
        if user.role != "teacher":
            return Response({"error": "Access denied. Only teachers can log in."}, status=403)

        # ✅ Compare plain-text passwords directly
        if user.password != password:
            return Response({"error": "Invalid username or password."}, status=401)

        # ✅ Generate JWT access token
        access_token = AccessToken.for_user(user)

        return Response({
            "message": "✅ Teacher login successful!",
            "username": user.username,
            "linked_id": user.linked_id,
            "role": user.role,
            "access": str(access_token),
        }, status=200)


# ✅ 1️⃣ Create Subject
class CreateSubjectAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def post(self, request):
        subject_data = {
            "code": request.data.get("code"),
            "name": request.data.get("name"),
            "teacher_id": request.data.get("teacher_id"),
        }

        serializer = SubjectSerializer(data=subject_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "✅ Subject created successfully!"}, status=201)
        return Response(serializer.errors, status=400)


# ✅ 2️⃣ Create Session (Generate QR)
class CreateSessionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def post(self, request):
        session_data = {
            "subject_id": request.data.get("subject_id"),
            "topic": request.data.get("topic"),
            "class_date": request.data.get("class_date"),
            "start_time": request.data.get("start_time"),
            "end_time": request.data.get("end_time"),
        }

        serializer = SessionSerializer(data=session_data)
        if serializer.is_valid():
            session = serializer.save()

            # ✅ Use subject.code instead of subject.id
            qr_path = generate_session_qr(
                subject_code=session.subject.code,  # <-- fixed here
                session_id=session.id,
                topic=session.topic,
                class_date=str(session.class_date),
                start_time=str(session.start_time),
            )

            return Response(
                {
                    "message": "✅ Session created successfully!",
                    "qr_code_path": qr_path,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ✅ 3️⃣ View My Subjects
class TeacherSubjectsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def get(self, request, teacher_id):
        subjects = Subject.objects.filter(teacher_id=teacher_id).order_by("code")
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=200)


# ✅ 4️⃣ View Sessions for a Subject
class SubjectSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def get(self, request, subject_id):
        sessions = Session.objects.filter(subject_id=subject_id).order_by("-class_date")
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data, status=200)


# ✅ 5️⃣ View Attendance Records
class SubjectAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def get(self, request, subject_id):
        attendance = Attendance.objects.filter(session__subject_id=subject_id)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data, status=200)


# ✅ 6️⃣ Check Attendance % for a Specific Student
# ✅ Fixed StudentAttendancePercentageAPIView
class StudentAttendancePercentageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def get(self, request, subject_id, student_id):
        queryset = Attendance.objects.filter(
            session__subject_id=subject_id, student__student_id=student_id
        )

        total_classes = queryset.count()
        attended_classes = queryset.filter(status="Present").count()

        if total_classes == 0:
            return Response({"message": "No attendance records found."}, status=404)

        percentage = round((attended_classes / total_classes) * 100, 2)

        subject = Subject.objects.filter(id=subject_id).first()
        subject_code = subject.code if subject else "N/A"

        data = {
            "student_id": student_id,
            "subject_code": subject_code,  # ✅ matches serializer field
            "total_classes": total_classes,
            "attended": attended_classes,
            "percentage": percentage,
        }

        serializer = AttendancePercentageSerializer(data)
        return Response(serializer.data if serializer else data, status=200)


class SubjectAllStudentsAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherUserCustom]

    def get(self, request, subject_id):
        # ✅ Fetch attendance summary per student for a given subject
        attendance_summary = (
            Attendance.objects
            .filter(session__subject_id=subject_id)
            .values("student__student_id")
            .annotate(
                total_classes=Count("id"),
                attended=Count("id", filter=Q(status="Present"))
            )
            .order_by("student__student_id")
        )

        if not attendance_summary:
            return Response({"message": "No attendance data found."}, status=404)

        # ✅ Normalize data for serializer
        formatted_data = []
        subject = Subject.objects.filter(id=subject_id).first()
        subject_code = subject.code if subject else "Unknown"

        for record in attendance_summary:
            total = record["total_classes"]
            attended = record["attended"]
            percentage = round((attended / total) * 100, 2) if total else 0.0

            formatted_data.append({
                "subject_code": subject_code,                # ✅ Added this field
                "student_id": record["student__student_id"], # ✅ Renamed
                "total_classes": total,
                "attended": attended,
                "percentage": percentage,
            })

        serializer = AttendancePercentageSerializer(formatted_data, many=True)
        return Response(serializer.data, status=200)
