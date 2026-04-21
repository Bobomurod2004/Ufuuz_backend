from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.utils import timezone
from .models import Category, News, NewsImage, NewsVideo


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

    def test_slug_is_generated_for_each_language(self):
        category = Category.objects.create(title='General')

        news = News.objects.create(
            category=category,
            title_uz='Talaba hayoti',
            title_en='Student Life',
            title_fr='Vie etudiante',
            content_uz='Matn',
            content_en='Content',
            content_fr='Contenu',
        )

        self.assertEqual(news.slug_uz, 'talaba-hayoti')
        self.assertEqual(news.slug_en, 'student-life')
        self.assertEqual(news.slug_fr, 'vie-etudiante')
        self.assertEqual(news.slug, 'talaba-hayoti')

    def test_news_video_requires_file_or_url(self):
        category = Category.objects.create(title='General')
        news = News.objects.create(
            category=category,
            title='Video News',
            content='Video content',
        )

        with self.assertRaises(ValidationError):
            NewsVideo.objects.create(news=news)


class NewsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.published_at = timezone.make_aware(datetime(2026, 4, 15, 10, 30, 0))
        self.category = Category.objects.create(
            title_uz='Yangilik',
            title_en='News',
            title_fr='Actualite',
        )
        self.other_category = Category.objects.create(
            title_uz='Tadbirlar',
            title_en='Events',
            title_fr='Evenements',
        )
        self.news = News.objects.create(
            category=self.category,
            slug='campus-update',
            title_uz='Kampus yangiligi',
            title_en='Campus Update',
            title_fr='Mise a jour du campus',
            summary_uz='Qisqa izoh',
            summary_en='Short summary',
            summary_fr='Resume court',
            content_uz='Birinchi abzas\n\nIkkinchi abzas',
            content_en='First paragraph\n\nSecond paragraph',
            content_fr='Premier paragraphe\n\nDeuxieme paragraphe',
            published_at=self.published_at,
            is_published=True,
        )
        self.other_news = News.objects.create(
            category=self.other_category,
            title_uz='Laboratoriya ochilishi',
            title_en='Laboratory Opening',
            title_fr='Ouverture du laboratoire',
            summary_uz='Ikkinchi yangilik',
            summary_en='Second news',
            summary_fr='Deuxieme actualite',
            content_uz='Ikkinchi kontent',
            content_en='Second content',
            content_fr='Deuxieme contenu',
            published_at=timezone.make_aware(datetime(2026, 4, 14, 8, 0, 0)),
            is_published=True,
        )
        NewsImage.objects.create(
            news=self.news,
            image='news/gallery/test-image.jpg',
            caption_uz='Asosiy galereya rasmi',
            caption_en='Gallery image',
            order=1,
        )
        NewsVideo.objects.create(
            news=self.news,
            title_uz='Yangilik videosi',
            title_en='News video',
            video_url='https://example.com/video.mp4',
            order=1,
        )

    def test_news_list_has_language_metadata_and_short_description(self):
        response = self.client.get('/api/v1/news/news/?lang=en', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Language'], 'en')

        payload = response.json()
        self.assertEqual(payload['language'], 'en')
        self.assertTrue(payload['results'])

        first_item = payload['results'][0]
        self.assertEqual(first_item['title'], 'Campus Update')
        self.assertEqual(first_item['short_description'], 'Short summary')
        self.assertTrue(first_item['published_at'].startswith('2026-04-15T10:30:00'))
        self.assertNotIn('content', first_item)

    def test_news_list_can_be_filtered_by_category(self):
        response = self.client.get(
            f'/api/v1/news/news/?lang=en&category={self.category.id}',
            secure=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Language'], 'en')

        payload = response.json()
        self.assertEqual(payload['language'], 'en')
        self.assertEqual(payload['count'], 1)
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(payload['results'][0]['id'], self.news.id)
        self.assertEqual(payload['results'][0]['category'], self.category.id)

    def test_news_list_with_invalid_category_filter_returns_empty(self):
        response = self.client.get('/api/v1/news/news/?lang=en&category=abc', secure=True)
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload['count'], 0)
        self.assertEqual(payload['results'], [])

    def test_news_detail_by_slug_returns_full_content_media_and_paragraphs(self):
        response = self.client.get('/api/v1/news/news/campus-update/?lang=en', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Language'], 'en')

        payload = response.json()
        self.assertEqual(payload['title'], 'Campus Update')
        self.assertTrue(payload['published_at'].startswith('2026-04-15T10:30:00'))
        self.assertEqual(payload['content'], 'First paragraph\n\nSecond paragraph')
        self.assertEqual(payload['content_paragraphs'], ['First paragraph', 'Second paragraph'])
        self.assertEqual(len(payload['images']), 1)
        self.assertEqual(len(payload['videos']), 1)
        self.assertEqual(payload['videos'][0]['source'], 'https://example.com/video.mp4')

    def test_news_detail_by_id_returns_full_content(self):
        response = self.client.get(f'/api/v1/news/news/by-id/{self.news.id}/?lang=en', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Language'], 'en')

        payload = response.json()
        self.assertEqual(payload['slug'], 'campus-update')
        self.assertIn('content', payload)

    def test_news_detail_by_slug_uses_requested_language_slug(self):
        localized_news = News.objects.create(
            category=self.category,
            title_uz='Talaba hayoti',
            title_en='Student Life',
            title_fr='Vie etudiante',
            summary_uz='Uz summary',
            summary_en='En summary',
            summary_fr='Fr summary',
            content_uz='Uz content',
            content_en='En content',
            content_fr='Fr content',
            is_published=True,
        )

        en_response = self.client.get('/api/v1/news/news/student-life/?lang=en', secure=True)
        self.assertEqual(en_response.status_code, 200)
        self.assertEqual(en_response.json()['id'], localized_news.id)
        self.assertEqual(en_response.json()['slug'], 'student-life')

        fr_response = self.client.get('/api/v1/news/news/vie-etudiante/?lang=fr', secure=True)
        self.assertEqual(fr_response.status_code, 200)
        self.assertEqual(fr_response.json()['id'], localized_news.id)
        self.assertEqual(fr_response.json()['slug'], 'vie-etudiante')
