# Generated by Django 3.1.5 on 2021-07-13 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_auto_20210629_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.cdekoffice', verbose_name='Офис'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата/Время'),
        ),
    ]
