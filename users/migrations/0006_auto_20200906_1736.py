# Generated by Django 3.0.5 on 2020-09-06 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200902_0746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationshiprequest',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]