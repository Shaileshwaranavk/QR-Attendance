from django.urls import path
from core.views.teacher_views import (
    CreateSubjectAPIView,
    CreateSessionAPIView,
    TeacherSubjectsAPIView,
    SubjectSessionsAPIView,
    SubjectAttendanceAPIView,
    StudentAttendancePercentageAPIView,
    SubjectAllStudentsAttendanceAPIView,
    TeacherLoginAPIView
)

urlpatterns = [
    path('login/', TeacherLoginAPIView.as_view(), name='teacher-login'),
    path('create-subject/', CreateSubjectAPIView.as_view(), name='create-subject'),
    path('create-session/', CreateSessionAPIView.as_view(), name='create-session'),
    path('subjects/<str:teacher_id>/', TeacherSubjectsAPIView.as_view(), name='teacher-subjects'),
    path('sessions/<int:subject_id>/', SubjectSessionsAPIView.as_view(), name='subject-sessions'),
    path('attendance/<int:subject_id>/', SubjectAttendanceAPIView.as_view(), name='subject-attendance'),
    path('attendance/<int:subject_id>/<str:student_id>/', StudentAttendancePercentageAPIView.as_view(), name='student-attendance-percent'),
    path('attendance-summary/<int:subject_id>/', SubjectAllStudentsAttendanceAPIView.as_view(), name='subject-all-students'),
]
