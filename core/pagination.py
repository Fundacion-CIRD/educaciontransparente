from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class SitePagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 100

    def get_paginated_response(self, data):
        if "reports" not in self.request.path:
            return super().get_paginated_response(data)

        return Response(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
                "summary": {
                    "total_disbursed": "255.000.000",
                    "total_accounted_for": "365.000.000",
                },
            }
        )
