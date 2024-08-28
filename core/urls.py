from rest_framework import routers

from core.views import InstitutionViewSet, DepartmentViewSet, DistrictViewSet

router = routers.SimpleRouter()

router.register("institutions", InstitutionViewSet)
router.register("departments", DepartmentViewSet)
router.register("districts", DistrictViewSet)

urlpatterns = router.urls
