from rest_framework import routers

from accountability.views import (
    ReportViewSet,
    DisbursementViewSet,
    ReceiptViewSet,
    AccountObjectChartViewSet,
    ReceiptItemViewSet,
    ResolutionViewSet,
)

router = routers.SimpleRouter()

router.register("resolutions", ResolutionViewSet)
router.register("disbursements", DisbursementViewSet)
router.register("reports", ReportViewSet)
router.register("receipts", ReceiptViewSet)
router.register("account-objects", AccountObjectChartViewSet)
router.register("receipt-items", ReceiptItemViewSet)

urlpatterns = router.urls
