# Generated by Django 5.0.7 on 2024-10-18 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sale", "0004_rename_sale_id_refund_sale_refund_so"),
    ]

    operations = [
        migrations.AlterField(
            model_name="refund",
            name="so",
            field=models.CharField(max_length=30),
        ),
    ]
