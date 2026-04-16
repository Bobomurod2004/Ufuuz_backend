from django.test import TestCase
from .models import Category, News


class NewsModelTests(TestCase):
    def test_slug_is_generated_and_disambiguated(self):
        category = Category.objects.create(title='General')

        first_news = News.objects.create(
            category=category,
            title='Campus Update',
            content='First content',
        )
        second_news = News.objects.create(
            category=category,
            title='Campus Update',
            content='Second content',
        )

        self.assertEqual(first_news.slug, 'campus-update')
        self.assertEqual(second_news.slug, 'campus-update-2')
