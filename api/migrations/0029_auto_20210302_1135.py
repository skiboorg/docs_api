# Generated by Django 3.1.5 on 2021-03-02 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_itemsize_order_num'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemsize',
            options={'verbose_name': 'Размер', 'verbose_name_plural': '5.1. Размеры'},
        ),
        migrations.AddField(
            model_name='deliverytype',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Отображать??'),
        ),
    ]
