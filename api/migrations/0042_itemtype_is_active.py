# Generated by Django 3.1.5 on 2021-06-08 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20210520_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemtype',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, verbose_name='Отображать ?'),
        ),
    ]