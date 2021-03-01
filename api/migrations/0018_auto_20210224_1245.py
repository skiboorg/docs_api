# Generated by Django 3.1.5 on 2021-02-24 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20210221_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='code',
            field=models.IntegerField(null=True, verbose_name='Код города'),
        ),
        migrations.AlterField(
            model_name='city',
            name='price',
            field=models.IntegerField(blank=True, null=True, verbose_name='Стоимость доставки'),
        ),
        migrations.AlterField(
            model_name='item',
            name='name_slug',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]