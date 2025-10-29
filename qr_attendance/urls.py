from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin site
    path('admin/', admin.site.urls),

    # 🔹 API routes
    path('adminuser/', include('core.urls.admin_urls')),
    path('teacher/', include('core.urls.teacher_urls')),
    path('student/', include('core.urls.student_urls')),
]

# ✅ Serve media files (QR images, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
