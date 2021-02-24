# Generated by Django 3.1.5 on 2021-02-21 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20210214_1328'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'Товар в заказе', 'verbose_name_plural': 'Товары в заказах'},
        ),
        migrations.AddField(
            model_name='deliverytype',
            name='is_self_delivery',
            field=models.BooleanField(default=False, verbose_name='Это самовывоз?'),
        ),
    ]