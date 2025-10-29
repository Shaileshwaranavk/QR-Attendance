from django.urls import path
from core.views.student_views import (
    MarkAttendanceAPIView,
    OverallAttendanceAPIView,
    SubjectAttendanceAPIView,
    StudentLoginAPIView
)

urlpatterns = [
    path('login/', StudentLoginAPIView.as_view(), name='student-login'),
    path('mark-attendance/', MarkAttendanceAPIView.as_view(), name='mark-attendance'),
    path('attendance-overall/<str:student_id>/', OverallAttendanceAPIView.as_view(), name='overall-attendance'),
    path('attendance-subject/<str:student_id>/<str:subject_code>/', SubjectAttendanceAPIView.as_view(), name='subject-attendance'),
]
