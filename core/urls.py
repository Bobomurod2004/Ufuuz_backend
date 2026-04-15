from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path(settings.ADMIN_URL, admin.site.urls),
    prefix_default_language=False
)

# API v1 URLs
api_v1_patterns = [
    path('common/', include('apps.common.urls')),
    path('structure/', include('apps.structure.urls')),
    path('news/', include('apps.news.urls')),
    path('communications/', include('apps.communications.urls')),
]

urlpatterns += [
    path('api/v1/', include((api_v1_patterns, 'api_v1'), namespace='api_v1')),
]

if settings.ENABLE_API_DOCS:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
