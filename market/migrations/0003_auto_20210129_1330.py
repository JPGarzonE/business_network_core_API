# Generated by Django 3.0.5 on 2021-01-29 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_auto_20210107_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showcaseproduct',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
