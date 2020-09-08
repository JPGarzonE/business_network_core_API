# Generated by Django 3.0.5 on 2020-09-07 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', 'create_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycertificate',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='companysocialnetwork',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='employeesocialnetwork',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.Employee'),
        ),
        migrations.AlterField(
            model_name='productcertificate',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.Product'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='companies.Product'),
        ),
    ]