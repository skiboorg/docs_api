# Generated by Django 3.1.5 on 2021-06-29 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_itemtype_is_first'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemtype',
            options={'ordering': ('-is_first',), 'verbose_name': 'Вид товара', 'verbose_name_plural': '5. Виды товаров'},
        ),
        migrations.AddField(
            model_name='promocode',
            name='is_one_use',
            field=models.BooleanField(default=False, verbose_name='Одноразовый'),
        ),
        migrations.AddField(
            model_name='promocode',
            name='is_used',
            field=models.BooleanField(default=False, verbose_name='Использован'),
        ),
    ]