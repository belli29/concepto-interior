# Generated by Django 3.1.5 on 2021-01-21 21:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_preorderlineitem_delivery_cost'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preorderlineitem',
            old_name='delivery_cost',
            new_name='lineitem_delivery',
        ),
    ]
