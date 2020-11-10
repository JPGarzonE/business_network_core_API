# Generated by Django 3.0.5 on 2020-10-18 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0004_auto_20200906_1857'),
        ('market', '0003_auto_20201018_1346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='showcaseproduct',
            name='image_path',
        ),
        migrations.AddField(
            model_name='showcaseproduct',
            name='principal_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='multimedia.Image'),
        ),
    ]