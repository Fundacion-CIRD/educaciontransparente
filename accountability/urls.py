from rest_framework import routers

from accountability.views import ReportViewSet, DisbursementViewSet, ReceiptViewSet

router = routers.SimpleRouter()

router.register("disbursements", DisbursementViewSet)
router.register("reports", ReportViewSet)
router.register("receipts", ReceiptViewSet)

urlpatterns = router.urls
