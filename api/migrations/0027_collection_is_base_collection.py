# Generated by Django 3.1.5 on 2021-03-01 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20210301_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='is_base_collection',
            field=models.BooleanField(default=False, verbose_name='Это базовая колекция?'),
        ),
    ]
