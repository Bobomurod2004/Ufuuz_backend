from django.test import TestCase, Client
from django.conf import settings
from rest_framework import status
from apps.common.models import History, StaticPage
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

if __name__ == "__main__":
    pass
