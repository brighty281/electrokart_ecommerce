# Generated by Django 4.2.7 on 2024-01-17 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0042_rename_payment_method_orderplaced_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('Accepted', 'Accepted'), ('Packed', 'Packed'), ('On the way', 'On the way'), ('delivered', 'delivered'), ('Cancelled', 'Cancelled'), ('requested for cancellation', 'requested for cancellation'), ('requested for return', 'requested for return'), ('returned', 'returned')], default='pending', max_length=50),
        ),
    ]
