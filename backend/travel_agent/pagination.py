"""
Custom pagination classes for the Travel Agent API
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class ItemsPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that returns 'items' instead of 'results'.

    This matches the frontend's expected API contract.

    Response format:
    {
        "count": 100,
        "next": "http://api.example.org/accounts/?page=4",
        "previous": "http://api.example.org/accounts/?page=2",
        "items": [...]  # <-- Changed from 'results'
    }
    """
    page_size = 20
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return paginated response with 'items' key instead of 'results'"""
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('items', data)  # Changed from 'results' to 'items'
        ]))


class ResultsPageNumberPagination(PageNumberPagination):
    """
    Standard pagination class that returns 'results'.

    This is the default DRF behavior, kept for backwards compatibility.
    """
    page_size = 20
    page_size_query_param = 'pageSize'
    max_page_size = 100
