# Generated by Django 3.1.5 on 2021-05-04 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20210504_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='order_num',
            field=models.IntegerField(default=100, verbose_name='Номер по порядку'),
        ),
        migrations.AlterField(
            model_name='item',
            name='old_price',
            field=models.IntegerField(blank=True, default=0, verbose_name='Цена без скидки'),
        ),
    ]
