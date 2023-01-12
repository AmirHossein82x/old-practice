# Generated by Django 4.1.3 on 2022-12-04 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_orderitem_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_query_name='products_order', to='store.product'),
        ),
    ]
