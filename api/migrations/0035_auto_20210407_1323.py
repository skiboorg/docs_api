# Generated by Django 3.1.5 on 2021-04-07 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_category_is_at_menu'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='uid',
            field=models.IntegerField(default=0, verbose_name='UID'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='uid',
            field=models.IntegerField(default=0, verbose_name='UID'),
        ),
    ]