# Generated by Django 4.2.7 on 2023-12-30 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0023_orderplaced_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='sub_total',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
