# Generated by Django 4.2.7 on 2024-01-04 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0026_cart_is_paid_cart_razor_pay_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderplaced',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('Accepted', 'Accepted'), ('Packed', 'Packed'), ('On the way', 'On the way'), ('delivered', 'delivered'), ('Cancelled', 'Cancelled'), ('requested for cancellation', 'requested for cancellation'), ('requested for return', 'requested for return')], default='pending', max_length=50),
        ),
    ]
