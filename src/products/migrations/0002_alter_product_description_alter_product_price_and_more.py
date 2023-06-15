# Generated by Django 4.2.2 on 2023-06-13 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=1000),
        ),
        migrations.AlterField(
            model_name="product",
            name="summary",
            field=models.TextField(),
        ),
    ]