# Generated by Django 5.0.7 on 2024-07-31 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sale", "0002_order_discount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
