# Generated by Django 3.1.5 on 2021-03-25 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_category_is_at_home'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_at_menu',
            field=models.BooleanField(default=True, verbose_name='Показывать в меню'),
        ),
    ]