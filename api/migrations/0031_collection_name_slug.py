# Generated by Django 3.1.5 on 2021-03-02 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_collection_order_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='name_slug',
            field=models.CharField(blank=True, db_index=True, editable=False, max_length=255, null=True),
        ),
    ]
