# Generated by Django 5.0.7 on 2024-09-12 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sale", "0007_inlineorder_refunded"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="salereturnitem",
            name="sale_return",
        ),
        migrations.RemoveField(
            model_name="salereturnitem",
            name="item",
        ),
        migrations.DeleteModel(
            name="SaleReturn",
        ),
        migrations.DeleteModel(
            name="SaleReturnItem",
        ),
    ]