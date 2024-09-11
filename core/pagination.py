from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class SitePagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 100

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)
