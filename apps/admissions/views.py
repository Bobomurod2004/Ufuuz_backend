from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from .models import StudentApplication
from .serializers import StudentApplicationSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Talaba arizalari ro‘yxati',
    ),
    retrieve=extend_schema(
        summary='Talaba arizasi detali',
    ),
    create=extend_schema(
        summary='Talaba arizasini yuborish',
        description=(
            "Ariza yuborish uchun asosiy ma'lumotlar bilan birga "
            "`diploma_files` va `certificate_files` maydonlariga "
            "bir yoki bir nechta fayl yuborish mumkin."
        ),
    ),
)
@extend_schema(tags=['Admissions'])
class StudentApplicationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = StudentApplication.objects.prefetch_related(
        'diplomas',
        'certificates',
    ).order_by('-created_at')
    serializer_class = StudentApplicationSerializer
    parser_classes = (MultiPartParser, FormParser)
