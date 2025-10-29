from django.db import models, connection
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ✅ Custom User Manager (no password hashing)
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role=None, linked_id=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, role=role, linked_id=linked_id, **extra_fields)
        user.password = password  # 🚫 store as plain text (NOT recommended for production)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, role='admin', **extra_fields)


# ✅ Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # keep plain text
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ])
    linked_id = models.CharField(max_length=20, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username} ({self.role})"


# ✅ Teacher Table
class Teacher(models.Model):
    teacher_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.teacher_id} - {self.name}"


# ✅ Student Table
class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"


# ✅ Subject Table
class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return f"{self.code} - {self.name}"


# ✅ Session Table
class Session(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="sessions")
    topic = models.CharField(max_length=200)
    class_date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject.code} - {self.topic}"


# ✅ Attendance Table
class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendance_subjects")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_entries")
    status = models.CharField(max_length=10, default="Present")
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.student_id} → {self.session.subject.code}"



# ✅ Dynamic Table Creator (Optional)
def create_dynamic_attendance_table(subject_code: str):
    """
    Dynamically creates a subject-specific attendance table.
    Example: subject_code='CS101' → creates table 'attendance_cs101'
    """
    table_name = f"attendance_{subject_code.lower()}"
    with connection.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(20) REFERENCES core_student(student_id),
                date DATE DEFAULT CURRENT_DATE,
                status VARCHAR(10) DEFAULT 'Present'
            );
        """)
    print(f"✅ Dynamic table '{table_name}' verified/created successfully.")
