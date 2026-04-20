# Generated migration to remove Slider model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_simplified_slider_model'),
    ]

    operations = [
        # Remove Slider FK from SliderItem and delete Slider table
        migrations.RemoveField(
            model_name='slideritem',
            name='slider',
        ),
        migrations.DeleteModel(
            name='Slider',
        ),
    ]
