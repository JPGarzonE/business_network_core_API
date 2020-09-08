# Generated by Django 3.0.5 on 2020-09-02 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0002_document_verification'),
        ('companies', '0008_auto_20200902_0746'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='certificates',
            field=models.ManyToManyField(through='companies.ProductCertificate', to='companies.Certificate'),
        ),
        migrations.AddField(
            model_name='product',
            name='media',
            field=models.ManyToManyField(through='companies.ProductMedia', to='multimedia.Media'),
        ),
    ]