# Generated by Django 4.1.3 on 2022-12-18 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_cart_id_alter_cartitems_cart'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitems',
            unique_together={('cart', 'product')},
        ),
    ]
