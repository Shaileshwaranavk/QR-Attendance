from django.urls import path
from core.views.admin_views import (
    RegisterTeacherAPIView,
    RegisterStudentAPIView,
    ListTeachersAPIView,
    ListStudentsAPIView,
    StudentAttendanceSummaryAPIView,
    AllStudentsAttendanceAPIView,
    AdminLoginAPIView
)

urlpatterns = [
    path('login/', AdminLoginAPIView.as_view(), name='admin-login'),
    path('add-teacher/', RegisterTeacherAPIView.as_view(), name='add-teacher'),
    path('add-student/', RegisterStudentAPIView.as_view(), name='add-student'),
    path('teachers/', ListTeachersAPIView.as_view(), name='teachers-list'),
    path('students/', ListStudentsAPIView.as_view(), name='students-list'),
    path('student-attendance/<str:student_id>/', StudentAttendanceSummaryAPIView.as_view(), name='student-attendance'),
    path('all-attendance/', AllStudentsAttendanceAPIView.as_view(), name='all-students-attendance'),
]
