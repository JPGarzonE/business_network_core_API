from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_auto_20200907_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='multimedia.Image')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='companies.Product')),
            ],
            options={
                'db_table': 'productimage',
                'unique_together': {('product', 'image')},
            },
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(through='companies.ProductImage', to='multimedia.Image'),
        )
    ]