from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import Faculty, Department
from .serializers import FacultySerializer, DepartmentSerializer

@extend_schema(tags=['Structure'])
class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

@extend_schema(tags=['Structure'])
class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
