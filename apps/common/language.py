from collections import OrderedDict

from django.conf import settings
from django.utils import translation
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def get_supported_languages() -> tuple[tuple[str, str], ...]:
    return tuple((code, str(name)) for code, name in settings.LANGUAGES)


def get_supported_language_codes() -> tuple[str, ...]:
    return tuple(code for code, _ in get_supported_languages())


def get_default_language() -> str:
    default_language = getattr(
        settings,
        "MODELTRANSLATION_DEFAULT_LANGUAGE",
        settings.LANGUAGE_CODE,
    )
    supported_codes = get_supported_language_codes()
    if default_language in supported_codes:
        return default_language
    return supported_codes[0]


def build_language_query_parameter() -> OpenApiParameter:
    supported_codes = list(get_supported_language_codes())
    return OpenApiParameter(
        name="lang",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        enum=supported_codes,
        description=(
            "Javob tili. Agar yuborilsa `Accept-Language`dan ustun bo'ladi. "
            f"Qo'llab-quvvatlanadi: {', '.join(supported_codes)}."
        ),
    )


class QueryParameterLanguageMixin:
    language_query_param = "lang"

    def get_requested_language(self) -> str:
        supported_codes = get_supported_language_codes()
        requested_language = self.request.query_params.get(self.language_query_param)
        if requested_language:
            normalized_language = requested_language.strip().lower()
            if normalized_language in supported_codes:
                return normalized_language

        header_language = translation.get_language_from_request(
            self.request,
            check_path=False,
        )
        if header_language:
            normalized_header = header_language.strip().lower()
            if normalized_header in supported_codes:
                return normalized_header
            base_header = normalized_header.split("-", maxsplit=1)[0]
            if base_header in supported_codes:
                return base_header

        return get_default_language()

    def initial(self, request, *args, **kwargs):
        self._previous_language = translation.get_language()
        self._active_language = self.get_requested_language()
        translation.activate(self._active_language)
        request.LANGUAGE_CODE = self._active_language
        return super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        active_language = getattr(self, "_active_language", None)
        if active_language and hasattr(response, "headers"):
            response.headers["Content-Language"] = active_language

        previous_language = getattr(self, "_previous_language", None)
        if previous_language:
            translation.activate(previous_language)
        else:
            translation.deactivate()
        return response


class LanguageMetadataSerializerMixin(serializers.Serializer):
    language = serializers.SerializerMethodField()

    def get_language(self, obj) -> str:
        request = self.context.get("request")
        if request and getattr(request, "LANGUAGE_CODE", None):
            return request.LANGUAGE_CODE
        language = translation.get_language()
        return language or get_default_language()


class LanguageAwarePageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        current_language = (
            getattr(self.request, "LANGUAGE_CODE", None)
            or get_default_language()
        )

        return Response(
            OrderedDict(
                [
                    ("language", current_language),
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class LanguageAwareReadOnlyModelViewSet(
    QueryParameterLanguageMixin,
    viewsets.ReadOnlyModelViewSet,
):
    pagination_class = LanguageAwarePageNumberPagination
