# Generated by Django 3.1.5 on 2021-02-19 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0007_order_oxxo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='oxxo',
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('CC', 'Credit card'), ('OXXO', 'Oxxo voucher'), ('PP', 'PayPal')], default='CC', max_length=9),
        ),
    ]