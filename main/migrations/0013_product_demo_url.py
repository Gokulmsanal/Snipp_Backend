# Generated by Django 5.0.3 on 2024-04-13 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='demo_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
