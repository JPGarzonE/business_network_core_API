# Generated by Django 3.0.5 on 2020-09-06 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0003_image_video'),
        ('companies', '0009_auto_20200902_1553'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductMedia',
            new_name='ProductImage',
        ),
        migrations.RemoveField(
            model_name='certificate',
            name='image',
        ),
        migrations.RemoveField(
            model_name='dnaelement',
            name='media',
        ),
        migrations.RemoveField(
            model_name='importantevent',
            name='media',
        ),
        migrations.RemoveField(
            model_name='location',
            name='media',
        ),
        migrations.RemoveField(
            model_name='product',
            name='media',
        ),
        migrations.RemoveField(
            model_name='service',
            name='media',
        ),
        migrations.AddField(
            model_name='certificate',
            name='logo',
            field=models.ForeignKey(blank=True, help_text='Logo that represents the certificate authority', null=True, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
        ),
        migrations.AddField(
            model_name='dnaelement',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
        ),
        migrations.AddField(
            model_name='importantevent',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
        ),
        migrations.AddField(
            model_name='location',
            name='headquarters_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(through='companies.ProductImage', to='multimedia.Image'),
        ),
        migrations.AddField(
            model_name='productimage',
            name='image',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service',
            name='images',
            field=models.ManyToManyField(to='multimedia.Image'),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
        ),
        migrations.AlterUniqueTogether(
            name='productimage',
            unique_together={('product', 'image')},
        ),
        migrations.AlterModelTable(
            name='productimage',
            table='productimage',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='media',
        ),
    ]
