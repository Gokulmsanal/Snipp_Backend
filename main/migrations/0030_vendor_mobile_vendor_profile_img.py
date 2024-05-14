# Generated by Django 5.0.3 on 2024-04-25 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_alter_customeraddress_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='mobile',
            field=models.PositiveBigIntegerField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='profile_img',
            field=models.ImageField(null=True, upload_to='seller_imgs/'),
        ),
    ]
