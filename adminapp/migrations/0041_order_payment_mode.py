# Generated by Django 4.2.7 on 2024-01-16 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0040_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_mode',
            field=models.CharField(default='Cash on Delivery', max_length=100),
        ),
    ]
