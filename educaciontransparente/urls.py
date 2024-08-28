from django.contrib import admin
from django.urls import path, include

api_urlpatterns = [
    path("", include("core.urls")),
    path("", include("accountability.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns), name="api"),
    path("", include("website.urls"), name="website"),
]

admin.site.site_header = "Panel de administración"
admin.site.site_title = "Panel de administración"
admin.site.index_title = "Bienvenid@ al panel de administración"
