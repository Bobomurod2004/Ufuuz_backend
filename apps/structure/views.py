from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Faculty, Department
from .serializers import FacultySerializer, DepartmentSerializer

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['Structure'])
class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.prefetch_related('departments')
    serializer_class = FacultySerializer

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['Structure'])
class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.select_related('faculty')
    serializer_class = DepartmentSerializer
