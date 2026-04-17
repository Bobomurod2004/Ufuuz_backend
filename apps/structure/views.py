from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.common.language import (
    LanguageAwareReadOnlyModelViewSet,
    build_language_query_parameter,
)
from .models import Faculty, Department
from .serializers import FacultySerializer, DepartmentSerializer

LANGUAGE_QUERY_PARAMETER = build_language_query_parameter()

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Structure'])
class FacultyViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = Faculty.objects.prefetch_related('departments').order_by('id')
    serializer_class = FacultySerializer

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Structure'])
class DepartmentViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = Department.objects.select_related('faculty').order_by('id')
    serializer_class = DepartmentSerializer
