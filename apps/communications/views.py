from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Contact, SocialLink
from .serializers import ContactSerializer, SocialLinkSerializer

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['Communications'])
class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
@extend_schema(tags=['Communications'])
class SocialLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
