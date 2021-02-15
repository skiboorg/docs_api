# Generated by Django 3.1.5 on 2021-02-14 08:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0013_auto_20210207_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_in_feed',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Выгружать товар ?'),
        ),
        migrations.AlterField(
            model_name='item',
            name='is_active',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Отображать товар ?'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment', models.CharField(blank=True, max_length=50, null=True)),
                ('delivery', models.CharField(blank=True, max_length=50, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('total_price', models.IntegerField(default=0, verbose_name='Общая стоимость заказа')),
                ('weight', models.IntegerField(default=0)),
                ('track_code', models.CharField(blank=True, max_length=50, null=True, verbose_name='Трек код')),
                ('order_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='Код заказа')),
                ('is_complete', models.BooleanField(default=False, verbose_name='Заказ выполнен ?')),
                ('is_payed', models.BooleanField(default=False, verbose_name='Заказ оплачен ?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Заказ клиента')),
                ('guest', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.guest', verbose_name='Заказ гостя')),
                ('promo_code', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.promocode', verbose_name='Использованный промо-код')),
            ],
        ),
    ]
