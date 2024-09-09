from django.urls import path

from website import views

urlpatterns = [
    path("", views.index, name="index"),
    path("quienes-somos/", views.quienes_somos, name="quienes_somos"),
    path("open-data/", views.open_data, name="open_data"),
    path("recursos/", views.resources, name="resources"),
    path(
        "instituciones/<int:pk>/",
        views.InstitutionDetailsView.as_view(),
        name="institution_details",
    ),
    path(
        "instituciones/<int:institution_id>/rendiciones/<int:report_id>/",
        views.ReportDetailView.as_view(),
        name="report_detail",
    ),
    path("export/", views.export_to_csv, name="export_csv"),
]
