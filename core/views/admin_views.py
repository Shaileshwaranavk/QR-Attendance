from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Teacher, Student, User, Subject, Attendance
from core.serializers import (
    TeacherSerializer,
    StudentSerializer,
    UserSerializer,
    AttendancePercentageSerializer
)
from core.permissions import IsAdminUserCustom
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Count, Q, F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from core.models import User

from rest_framework.permissions import IsAuthenticated, AllowAny

class AdminLoginAPIView(APIView):
    
    permission_classes = [AllowAny]
    
    """
    Admin login — verifies plain-text credentials and returns a JWT access token.
    """

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required."}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password."}, status=401)

        # ✅ Make sure user is admin
        if user.role != "admin":
            return Response({"error": "Only admins can log in."}, status=403)

        # ✅ Plain-text password check (no hashing)
        if user.password != password:
            return Response({"error": "Invalid username or password."}, status=401)

        # ✅ Generate JWT token
        token = AccessToken.for_user(user)

        return Response({
            "message": "✅ Admin login successful!",
            "username": user.username,
            "role": user.role,
            "access": str(token)
        }, status=200)

# ✅ Register Teacher
class RegisterTeacherAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def post(self, request):
        teacher_data = {
            "teacher_id": request.data.get("teacher_id"),
            "name": request.data.get("name"),
            "department": request.data.get("department"),
            "email": request.data.get("email"),
        }

        teacher_serializer = TeacherSerializer(data=teacher_data)
        if teacher_serializer.is_valid():
            teacher = teacher_serializer.save()

            user_data = {
                "username": request.data.get("username"),
                "password": request.data.get("password"),
                "role": "teacher",
                "linked_id": teacher.teacher_id,
            }

            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response({"message": "✅ Teacher added successfully!"}, status=201)

            return Response(user_serializer.errors, status=400)
        return Response(teacher_serializer.errors, status=400)


# ✅ Register Student
class RegisterStudentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def post(self, request):
        student_data = {
            "student_id": request.data.get("student_id"),
            "name": request.data.get("name"),
            "department": request.data.get("department"),
            "email": request.data.get("email"),
        }

        student_serializer = StudentSerializer(data=student_data)
        if student_serializer.is_valid():
            student = student_serializer.save()

            user_data = {
                "username": request.data.get("username"),
                "password": request.data.get("password"),
                "role": "student",
                "linked_id": student.student_id,
            }

            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response({"message": "✅ Student registered successfully!"}, status=201)
            return Response(user_serializer.errors, status=400)

        return Response(student_serializer.errors, status=400)


# ✅ View Student Attendance (ORM-based)
class StudentAttendanceSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request, student_id):
        # Group attendance by subject for a specific student
        attendance_data = (
            Attendance.objects
            .filter(student__student_id=student_id)
            .values(
                "session__subject__code",  # subject code
                "student__student_id"      # student id
            )
            .annotate(
                total_classes=Count("id"),
                attended=Count("id", filter=Q(status="Present"))
            )
        )

        if not attendance_data:
            return Response(
                {"message": "No attendance records found for this student."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ Rename for serializer compatibility
        results = []
        for record in attendance_data:
            total = record["total_classes"]
            attended = record["attended"]
            percentage = round((attended / total) * 100, 2) if total else 0.0

            results.append({
                "student_id": record["student__student_id"],
                "subject_code": record["session__subject__code"],
                "total_classes": total,
                "attended": attended,
                "percentage": percentage
            })

        serializer = AttendancePercentageSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ View All Students Attendance Summary (ORM-based)
class AllStudentsAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        # Get attendance summary grouped by student and subject
        attendance_data = (
            Attendance.objects
            .values("student__student_id", "session__subject__code")
            .annotate(
                total_classes=Count("id"),
                attended=Count("id", filter=Q(status="Present"))
            )
            .order_by("student__student_id", "session__subject__code")
        )

        if not attendance_data:
            return Response(
                {"message": "No attendance data found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ Normalize key names for serializer compatibility
        results = []
        for record in attendance_data:
            total = record["total_classes"]
            attended = record["attended"]
            percentage = round((attended / total) * 100, 2) if total else 0.0

            results.append({
                "student_id": record["student__student_id"],
                "subject_code": record["session__subject__code"],
                "total_classes": total,
                "attended": attended,
                "percentage": percentage,
            })

        serializer = AttendancePercentageSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ View All Teachers
class ListTeachersAPIView(APIView):
    """
    Allows admin to view all registered teachers.
    """
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        teachers = Teacher.objects.all().order_by("teacher_id")
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ View All Students
class ListStudentsAPIView(APIView):
    """
    Allows admin to view all registered students.
    """
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        students = Student.objects.all().order_by("student_id")
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
