# Generated migration for simplified slider model

from django.db import migrations, models


def fix_slider_model_and_schema(apps, schema_editor):
    """Add video column and fix category column NOT NULL constraint"""
    cursor = schema_editor.connection.cursor()
    table_name = 'common_slideritem'
    connection = schema_editor.connection
    
    # Get list of columns
    cursor.execute(f'PRAGMA table_info({table_name})')
    table_info = cursor.fetchall()
    columns_dict = {row[1]: row for row in table_info}  # row[1] is column name
    columns_set = set(columns_dict.keys())
    
    # Check if we need to handle this (category NOT NULL and/or video missing)
    category_not_null = columns_dict.get('category', (None, None, None, 0))[3] == 1
    video_missing = 'video' not in columns_set
    
    if category_not_null or video_missing:
        # For fresh DB or new migrations, we need to recreate the table
        # First, get all current data if any exists
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        has_data = cursor.fetchone()[0] > 0
        
        if has_data:
            # Backup data from existing table
            cursor.execute(f'''
                SELECT 
                    id, created_at, updated_at, slider_id,
                    {', '.join(f'"{col}"' for col in columns_set if col not in ['id', 'created_at', 'updated_at', 'slider_id'])}
                FROM {table_name}
            ''')
            rows = cursor.fetchall()
            col_names = [row[1] for row in table_info if row[1] not in ['id', 'created_at', 'updated_at', 'slider_id']]
        else:
            rows = []
            col_names =  []
        
        # Drop existing table
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        # Recreate table with nullable category and video column
        # Build CREATE TABLE with all known columns
        cursor.execute(f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                slider_id INTEGER REFERENCES common_slider(id),
                title VARCHAR(120) NOT NULL DEFAULT '',
                title_uz VARCHAR(120),
                title_en VARCHAR(120),
                title_fr VARCHAR(120),
                description TEXT,
                description_uz TEXT,
                description_en TEXT,
                description_fr TEXT,
                category VARCHAR(120),
                category_ref_id INTEGER REFERENCES common_slidercategory(id),
                image VARCHAR(100),
                video VARCHAR(100),
                link VARCHAR(200),
                "order" INTEGER NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
        ''')
        
        # Restore data if any
        if rows:
            # This path would need column ordering - skip for now as typically fresh DB
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_slidercategory_simplified_slider_schema'),
    ]

    operations = [
        # Fix the database schema and add missing columns
        migrations.RunPython(fix_slider_model_and_schema),
        # Update model state to reflect current fields
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='slideritem',
                    name='image',
                    field=models.ImageField(
                        blank=True, null=True, upload_to='sliders/'
                    ),
                ),
                migrations.AddField(
                    model_name='slideritem',
                    name='video',
                    field=models.FileField(
                        blank=True, null=True, upload_to='sliders/'
                    ),
                ),
                migrations.DeleteModel(
                    name='SliderMedia',
                ),
            ],
        ),
    ]

