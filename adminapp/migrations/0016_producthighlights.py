# Generated by Django 4.2.7 on 2023-12-19 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0015_product_variant_feature'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductHighlights',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('highlight', models.CharField(blank=True, max_length=200, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.product')),
            ],
        ),
    ]