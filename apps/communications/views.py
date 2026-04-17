from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.common.language import (
    LanguageAwareReadOnlyModelViewSet,
    build_language_query_parameter,
)
from .models import Contact, SocialLink
from .serializers import ContactSerializer, SocialLinkSerializer

LANGUAGE_QUERY_PARAMETER = build_language_query_parameter()

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Communications'])
class ContactViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = Contact.objects.all().order_by('id')
    serializer_class = ContactSerializer

@extend_schema_view(
    list=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
    retrieve=extend_schema(parameters=[LANGUAGE_QUERY_PARAMETER]),
)
@extend_schema(tags=['Communications'])
class SocialLinkViewSet(LanguageAwareReadOnlyModelViewSet):
    queryset = SocialLink.objects.all().order_by('id')
    serializer_class = SocialLinkSerializer
