# Generated by Django 4.2.7 on 2023-12-27 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0021_alter_orderplaced_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderplaced',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('Accepted', 'Accepted'), ('Packed', 'Packed'), ('On the way', 'On the way'), ('delivered', 'delivered'), ('Cancelled', 'Cancelled'), ('requested for cancellation', 'requested for cancellation')], default='pending', max_length=50),
        ),
    ]
