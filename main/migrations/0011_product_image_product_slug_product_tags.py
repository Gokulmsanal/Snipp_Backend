# Generated by Django 5.0.3 on 2024-04-11 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_productimage_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(null=True, upload_to='product_imgs/'),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.CharField(max_length=300, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.TextField(null=True),
        ),
    ]
