# Generated by Django 5.0.7 on 2024-07-15 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_cake_image_alter_cake_flavor_alter_cake_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cake',
            name='image',
            field=models.ImageField(default='default_image.jpg', upload_to='cakes/'),
        ),
        migrations.AlterField(
            model_name='cake',
            name='flavor',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='cake',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='cake',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='cake',
            name='size',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(default='default_image.jpg', upload_to='cake_images/'),
        ),
    ]
