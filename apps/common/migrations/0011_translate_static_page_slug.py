from django.db import migrations, models
from django.utils.text import slugify


TRANSLATED_SLUG_FIELDS = ('slug_uz', 'slug_en', 'slug_fr')


def _normalize_slug(base_slug, max_length, suffix=None):
    if not base_slug:
        base_slug = 'page'

    if suffix is None:
        return base_slug[:max_length]

    suffix_text = f'-{suffix}'
    allowed = max_length - len(suffix_text)
    if allowed < 1:
        return suffix_text[-max_length:]
    return f"{base_slug[:allowed]}{suffix_text}"


def _build_unique_slug(StaticPage, instance, field_name, source_value):
    max_length = StaticPage._meta.get_field(field_name).max_length or 50
    base_slug = slugify(source_value) or 'page'
    candidate = _normalize_slug(base_slug, max_length)
    suffix = 2

    while StaticPage.objects.filter(**{field_name: candidate}).exclude(pk=instance.pk).exists():
        candidate = _normalize_slug(base_slug, max_length, suffix=suffix)
        suffix += 1

    return candidate


def populate_translated_static_page_slugs(apps, schema_editor):
    StaticPage = apps.get_model('common', 'StaticPage')

    for page in StaticPage.objects.all().order_by('pk'):
        existing_slug = (page.slug or '')
        if existing_slug:
            existing_slug = _build_unique_slug(
                StaticPage,
                page,
                'slug',
                existing_slug,
            )

        if not page.slug_uz:
            source_title = page.title_uz or page.title or existing_slug or 'page'
            page.slug_uz = existing_slug or _build_unique_slug(
                StaticPage,
                page,
                'slug_uz',
                source_title,
            )

        for language_code in ('en', 'fr'):
            field_name = f'slug_{language_code}'
            if getattr(page, field_name):
                continue

            source_title = (
                getattr(page, f'title_{language_code}', None)
                or page.title_uz
                or page.title
                or page.slug_uz
                or existing_slug
                or 'page'
            )
            setattr(
                page,
                field_name,
                _build_unique_slug(
                    StaticPage,
                    page,
                    field_name,
                    source_title,
                ),
            )

        if not page.slug:
            page.slug = page.slug_uz or _build_unique_slug(
                StaticPage,
                page,
                'slug',
                page.title_uz or page.title or 'page',
            )
        else:
            page.slug = _build_unique_slug(StaticPage, page, 'slug', page.slug)

        page.save(update_fields=('slug',) + TRANSLATED_SLUG_FIELDS)


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_remove_slideritem_category_en_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticpage',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='slug_en',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='slug_fr',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='slug_uz',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.RunPython(
            populate_translated_static_page_slugs,
            migrations.RunPython.noop,
        ),
    ]
