# Generated by Django 3.1.5 on 2021-06-10 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_itemtype_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_need_pack',
            field=models.BooleanField(default=False, verbose_name='Нужна упаковка?'),
        ),
    ]
