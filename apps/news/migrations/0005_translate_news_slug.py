from django.db import migrations, models
from django.utils.text import slugify


TRANSLATED_SLUG_FIELDS = ('slug_uz', 'slug_en', 'slug_fr')


def _build_unique_slug(News, instance, field_name, source_value):
    base_slug = slugify(source_value) or 'news'
    candidate = base_slug
    suffix = 2

    while News.objects.filter(**{field_name: candidate}).exclude(pk=instance.pk).exists():
        candidate = f'{base_slug}-{suffix}'
        suffix += 1

    return candidate


def populate_translated_news_slugs(apps, schema_editor):
    News = apps.get_model('news', 'News')

    for news in News.objects.all().order_by('pk'):
        existing_slug = news.slug
        if not news.slug_uz:
            source_title = news.title_uz or news.title or existing_slug or 'news'
            news.slug_uz = existing_slug or _build_unique_slug(News, news, 'slug_uz', source_title)

        for language_code in ('en', 'fr'):
            field_name = f'slug_{language_code}'
            if getattr(news, field_name):
                continue

            source_title = (
                getattr(news, f'title_{language_code}', None)
                or news.title_uz
                or news.title
                or news.slug_uz
                or existing_slug
                or 'news'
            )
            setattr(
                news,
                field_name,
                _build_unique_slug(News, news, field_name, source_title),
            )

        if not news.slug:
            news.slug = news.slug_uz or _build_unique_slug(
                News,
                news,
                'slug',
                news.title_uz or news.title or 'news',
            )

        news.save(update_fields=('slug',) + TRANSLATED_SLUG_FIELDS)


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_alter_news_options_news_published_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='slug_en',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='news',
            name='slug_fr',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='news',
            name='slug_uz',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.RunPython(
            populate_translated_news_slugs,
            migrations.RunPython.noop,
        ),
    ]
