from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

api_urlpatterns = [
    path("", include("core.urls")),
    path("", include("accountability.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
    path("users/", include("users.urls")),
    path("", include("website.urls")),
]

if settings.ENVIRONMENT in ("local", "development"):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Panel de administración"
admin.site.site_title = "Panel de administración"
admin.site.index_title = "Bienvenid@ al panel de administración"
