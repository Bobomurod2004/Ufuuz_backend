from django.test import TestCase, Client
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from apps.common.models import (
    History,
    SliderCategory,
    SliderItem,
    StaticPage,
)
from apps.structure.models import Department, Faculty
from apps.news.models import Category, News
from apps.communications.models import Contact, SocialLink


class ApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed basic data
        self.history = History.objects.create(
            title_uz="Test History",
            content_uz="Content",
        )
        self.static_page = StaticPage.objects.create(
            title_uz="Sahifa",
            title_en="Page",
            slug="about-ufu",
            content_uz="Sahifa matni",
            content_en="Page content",
        )
        self.faculty = Faculty.objects.create(
            title_uz="Test Faculty",
            description_uz="Desc",
        )
        self.department = Department.objects.create(
            faculty=self.faculty,
            title_uz="Test Department",
            description_uz="Department desc",
        )
        self.category = Category.objects.create(title_uz="Test Category")
        self.news = News.objects.create(
            category=self.category,
            title_uz="Test News",
            title_en="Test News EN",
            slug="test-news",
            content_uz="Content",
            content_en="English content",
            is_published=True,
        )
        self.contact = Contact.objects.create(
            address_uz="Test Address",
            address_en="Test Address EN",
            phone="123",
            email="test@test.com",
        )
        self.social_link = SocialLink.objects.create(
            platform="Telegram",
            url="https://t.me/example",
        )

        self.slider_category = SliderCategory.objects.create(
            name_uz="Qabul bo'limi",
            name_en='Admission office',
            name_fr="Bureau d'admission",
            is_active=True,
            order=1,
        )
        image_path = default_storage.save(
            'sliders/test1.jpg',
            ContentFile(b'image-one'),
        )
        video_path = default_storage.save(
            'sliders/test-video.mp4',
            ContentFile(b'video-one'),
        )
        self.active_item = SliderItem.objects.create(
            category=self.slider_category,
            title_uz="Aktiv slide",
            title_en="Active slide",
            title_fr="Slide active",
            description_uz="Uzbekcha tavsif",
            description_en="English description",
            description_fr="Description francaise",
            image=image_path,
            video=video_path,
            is_active=True,
            order=1,
        )
        SliderItem.objects.create(
            category=self.slider_category,
            title_uz="Noaktiv slide",
            is_active=False,
            order=2,
        )

    def test_endpoints(self):
        endpoints = [
            '/api/v1/common/languages/',
            '/api/v1/common/history/',
            '/api/v1/common/pages/',
            '/api/v1/common/slider-categories/',
            '/api/v1/common/slider-items/',
            '/api/v1/structure/faculties/',
            '/api/v1/structure/departments/',
            '/api/v1/news/categories/',
            '/api/v1/news/news/',
            '/api/v1/communications/contact/',
            '/api/v1/communications/social-links/',
        ]

        if settings.ENABLE_API_DOCS:
            endpoints.extend([
                '/api/schema/',
                '/api/docs/',
            ])

        for url in endpoints:
            response = self.client.get(url, secure=True)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Failed at {url}",
            )

    def test_slider_endpoint_returns_only_active_items(self):
        response = self.client.get('/api/v1/common/slider-items/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertIn('results', payload)
        self.assertEqual(payload['count'], 1)
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(
            payload['results'][0]['title'],
            'Aktiv slide',
        )
        self.assertEqual(
            payload['results'][0]['category']['name'],
            "Qabul bo'limi",
        )
        self.assertEqual(
            payload['results'][0]['description'],
            'Uzbekcha tavsif',
        )
        self.assertTrue(
            payload['results'][0]['image'],
        )
        self.assertTrue(
            payload['results'][0]['video'],
        )

    def test_slider_fields_are_translated_by_lang(self):
        response = self.client.get(
            '/api/v1/common/slider-items/?lang=en',
            secure=True,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload['results'][0]['title'], 'Active slide')
        self.assertEqual(
            payload['results'][0]['category']['name'],
            'Admission office',
        )
        self.assertEqual(
            payload['results'][0]['description'],
            'English description',
        )

        response = self.client.get(
            '/api/v1/common/slider-items/?lang=fr',
            secure=True,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload['results'][0]['title'], 'Slide active')
        self.assertEqual(
            payload['results'][0]['category']['name'],
            "Bureau d'admission",
        )

    def test_media_url_is_served(self):
        media_path = default_storage.save(
            'sliders/test-media.txt',
            ContentFile(b'hello media'),
        )
        try:
            response = self.client.get(f'/media/{media_path}', secure=True)
            if settings.SERVE_MEDIA_FILES:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    b''.join(response.streaming_content),
                    b'hello media',
                )
            else:
                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND,
                )
        finally:
            if default_storage.exists(media_path):
                default_storage.delete(media_path)

    def test_language_param_is_available_for_other_apis(self):
        response = self.client.get(
            '/api/v1/structure/faculties/?lang=en',
            secure=True,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Language'], 'en')
        payload = response.json()
        self.assertEqual(payload['language'], 'en')

        response = self.client.get(
            '/api/v1/communications/contact/?lang=en',
            secure=True,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Language'], 'en')
        self.assertEqual(response.json()['language'], 'en')

    def test_id_based_retrieve_endpoints_are_visible_and_working(self):
        endpoints = [
            f'/api/v1/common/history/{self.history.id}/?lang=en',
            f'/api/v1/common/slider-items/{self.active_item.id}/?lang=en',
            f'/api/v1/structure/faculties/{self.faculty.id}/?lang=en',
            f'/api/v1/structure/departments/{self.department.id}/?lang=en',
            f'/api/v1/news/categories/{self.category.id}/?lang=en',
            f'/api/v1/communications/contact/{self.contact.id}/?lang=en',
            (
                f'/api/v1/communications/social-links/'
                f'{self.social_link.id}/?lang=en'
            ),
        ]
        for url in endpoints:
            response = self.client.get(url, secure=True)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Failed at {url}",
            )
            self.assertEqual(response['Content-Language'], 'en')

    def test_slug_based_endpoints_have_by_id_routes(self):
        page_response = self.client.get(
            f'/api/v1/common/pages/by-id/{self.static_page.id}/?lang=en',
            secure=True,
        )
        self.assertEqual(page_response.status_code, status.HTTP_200_OK)
        self.assertEqual(page_response['Content-Language'], 'en')
        self.assertEqual(page_response.json()['slug'], 'about-ufu')

        news_response = self.client.get(
            f'/api/v1/news/news/by-id/{self.news.id}/?lang=en',
            secure=True,
        )
        self.assertEqual(news_response.status_code, status.HTTP_200_OK)
        self.assertEqual(news_response['Content-Language'], 'en')
        payload = news_response.json()
        self.assertEqual(payload['slug'], 'test-news')
        self.assertIn('content', payload)

    def test_supported_languages_endpoint_returns_language_list(self):
        response = self.client.get('/api/v1/common/languages/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = response.json()
        self.assertIn('default_language', payload)
        self.assertIn('languages', payload)
        self.assertTrue(payload['languages'])

        language_codes = [item['code'] for item in payload['languages']]
        self.assertIn('uz', language_codes)
        self.assertIn('en', language_codes)
        self.assertIn('fr', language_codes)
