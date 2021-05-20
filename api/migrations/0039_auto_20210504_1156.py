# Generated by Django 3.1.5 on 2021-05-04 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_auto_20210504_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='discount',
            field=models.IntegerField(default=0, verbose_name='Скидка'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='discount',
            field=models.IntegerField(default=0, verbose_name='Скидка'),
        ),
        migrations.AlterField(
            model_name='item',
            name='discount_val',
            field=models.IntegerField(default=0, editable=False, verbose_name='Скидка'),
        ),
        migrations.AlterField(
            model_name='item',
            name='old_price',
            field=models.IntegerField(blank=True, default=0, editable=False, verbose_name='Цена без скидки'),
        ),
    ]