from django.test import TestCase, Client
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from apps.common.models import History, StaticPage, Slider, SliderItem
from apps.structure.models import Faculty, Department
from apps.news.models import Category, News
from apps.communications.models import Contact

class ApiTets(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed basic data
        History.objects.create(title_uz="Test History", content_uz="Content")
        self.faculty = Faculty.objects.create(title_uz="Test Faculty", description_uz="Desc")
        self.category = Category.objects.create(title_uz="Test Category")
        News.objects.create(category=self.category, title_uz="Test News", content_uz="Content", is_published=True)
        Contact.objects.create(address_uz="Test Address", phone="123", email="test@test.com")

        self.slider = Slider.objects.create(
            title="Asosiy slider",
            is_active=True,
            order=1,
        )
        SliderItem.objects.create(
            slider=self.slider,
            title="Aktiv slide",
            is_active=True,
            order=1,
            image='sliders/test1.jpg',
        )
        SliderItem.objects.create(
            slider=self.slider,
            title="Noaktiv slide",
            is_active=False,
            order=2,
            image='sliders/test2.jpg',
        )

    def test_endpoints(self):
        endpoints = [
            '/api/v1/common/history/',
            '/api/v1/common/pages/',
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed at {url}")
            print(f"✓ Checked {url} - Status 200")

    def test_slider_endpoint_returns_only_active_items(self):
        response = self.client.get('/api/v1/common/sliders/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(len(response.json()[0]['items']), 1)
        self.assertEqual(response.json()[0]['items'][0]['title'], 'Aktiv slide')

    def test_media_url_is_served(self):
        media_path = default_storage.save(
            'sliders/test-media.txt',
            ContentFile(b'hello media'),
        )
        try:
            response = self.client.get(f'/media/{media_path}', secure=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(b''.join(response.streaming_content), b'hello media')
        finally:
            if default_storage.exists(media_path):
                default_storage.delete(media_path)

if __name__ == "__main__":
    pass
