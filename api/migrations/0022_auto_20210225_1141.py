# Generated by Django 3.1.5 on 2021-02-25 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20210225_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='subcategory',
        ),
        migrations.AddField(
            model_name='collection',
            name='subcategory',
            field=models.ManyToManyField(blank=True, to='api.SubCategory', verbose_name='Относится к'),
        ),
    ]