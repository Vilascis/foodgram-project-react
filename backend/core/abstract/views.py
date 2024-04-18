from rest_framework import filters, viewsets


class AbstractViewset(viewsets.ModelViewSet):
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ["updated", "created"]
    ordering = ["-updated"]
