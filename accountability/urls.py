from rest_framework import routers

from accountability.views import (
    ReportViewSet,
    DisbursementViewSet,
    ReceiptViewSet,
    AccountObjectChartViewSet,
)

router = routers.SimpleRouter()

router.register("disbursements", DisbursementViewSet)
router.register("reports", ReportViewSet)
router.register("receipts", ReceiptViewSet)
router.register("account-objects", AccountObjectChartViewSet)

urlpatterns = router.urls
