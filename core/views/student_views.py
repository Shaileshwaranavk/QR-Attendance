from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Count, Q, F
from core.models import Attendance, Subject, Student, User, Session
from core.serializers import (
    AttendanceSerializer,
    AttendancePercentageSerializer,
)
from core.utils.qr_scanner import scan_qr
from core.permissions import IsStudentUserCustom

from rest_framework.permissions import IsAuthenticated, AllowAny

# ✅ 1️⃣ Student Login (Plaintext password version)
class StudentLoginAPIView(APIView):
    """
    Student login — verifies credentials and returns JWT access token.
    """
    
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ✅ Verify student role
        if user.role != "student":
            return Response(
                {"error": "Access denied. Only students can log in here."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ✅ Plain-text password check
        if user.password != password:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ✅ Generate JWT Token
        access_token = AccessToken.for_user(user)

        return Response(
            {
                "message": "✅ Student login successful!",
                "username": user.username,
                "linked_id": user.linked_id,
                "role": user.role,
                "access": str(access_token),
            },
            status=status.HTTP_200_OK,
        )


import cv2
import numpy as np
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Student, Subject, Session, Attendance
from core.serializers import AttendanceSerializer
from core.permissions import IsStudentUserCustom
from core.utils.qr_scanner import scan_qr  # ✅ use the updated scanner


class MarkAttendanceAPIView(APIView):
    """
    Student uploads or scans a QR code image to mark attendance.
    """

    permission_classes = [IsAuthenticated, IsStudentUserCustom]

    def post(self, request):
        student_id = request.data.get("student_id")
        qr_image = request.FILES.get("qr_image") or request.data.get("qr_image")

        # ✅ Validate input
        if not student_id or not qr_image:
            return Response(
                {"error": "Student ID and QR image are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Decode the QR code (works for both uploaded file and path)
        qr_result = scan_qr(qr_image, student_id=student_id)

        if not qr_result:
            return Response({"error": "Unable to decode QR code."}, status=400)

        # ✅ Expected structure from scan_qr()
        subject_code = qr_result["subject_code"]
        session_id = qr_result["session_id"]
        topic = qr_result["topic"]
        class_date = qr_result["class_date"]
        start_time = qr_result["start_time"]

        # ✅ Fetch student, subject, and session properly
        student = Student.objects.filter(student_id=student_id).first()
        subject = Subject.objects.filter(code=subject_code).first()
        session = Session.objects.filter(id=session_id, subject=subject).first()

        if not student:
            return Response({"error": "Student not found."}, status=404)

        if not subject or not session:
            return Response({"error": "Invalid or expired session."}, status=404)

        # ✅ Prevent duplicate attendance
        if Attendance.objects.filter(student=student, session=session).exists():
            return Response(
                {"message": "⚠️ Attendance already marked for this session."},
                status=status.HTTP_200_OK,
            )

        # ✅ Mark attendance
        attendance = Attendance.objects.create(
            student=student,
            session=session,
            subject=subject,
            status="Present",
        )

        serializer = AttendanceSerializer(attendance)
        return Response(
            {"message": "✅ Attendance marked successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


# ✅ 3️⃣ Overall Attendance (All Subjects)
class OverallAttendanceAPIView(APIView):
    """
    Student views total attendance percentage across all subjects.
    """
    permission_classes = [IsAuthenticated, IsStudentUserCustom]

    def get(self, request, student_id):
        attendance_data = (
            Attendance.objects
            .filter(student__student_id=student_id)
            .values(subject_code=F("session__subject__code"))
            .annotate(
                total_classes=Count("id"),
                attended=Count("id", filter=Q(status="Present"))
            )
        )

        if not attendance_data:
            return Response({"message": "No attendance data found."}, status=404)

        formatted_data = []
        for record in attendance_data:
            total = record["total_classes"]
            attended = record["attended"]
            percentage = round((attended / total) * 100, 2) if total else 0.0

            formatted_data.append({
                "student_id": student_id,               # ✅ add missing key
                "subject_code": record["subject_code"], # ✅ consistent field name
                "total_classes": total,
                "attended": attended,
                "percentage": percentage,
            })

        serializer = AttendancePercentageSerializer(formatted_data, many=True)
        return Response(serializer.data, status=200)



class SubjectAttendanceAPIView(APIView):
    """
    Student views attendance percentage for a specific subject.
    """
    permission_classes = [IsAuthenticated, IsStudentUserCustom]

    def get(self, request, student_id, subject_code):
        attendance_stats = (
            Attendance.objects
            .filter(student__student_id=student_id, session__subject__code=subject_code)
            .aggregate(
                total_classes=Count("id"),
                attended=Count("id", filter=Q(status="Present"))
            )
        )

        total = attendance_stats.get("total_classes") or 0
        attended = attendance_stats.get("attended") or 0

        if total == 0:
            return Response(
                {"message": "No attendance records found for this subject."},
                status=status.HTTP_404_NOT_FOUND,
            )

        percentage = round((attended / total) * 100, 2)

        data = {
            "student_id": student_id,
            "subject_code": subject_code,
            "total_classes": total,
            "attended": attended,
            "percentage": percentage,
        }

        # ✅ Proper serializer initialization with data dict
        serializer = AttendancePercentageSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
