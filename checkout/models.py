
import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import MinValueValidator
from django_countries.fields import CountryField
from products.models import Product
from profiles.models import UserProfile


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(
        max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    county = models.CharField(
        max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        default=''
        )
    shipped = models.BooleanField(default=False)
    pp_transaction_id = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        default=''
        )
    PAYMENT_CHOICES = [
        ('CC', 'Credit card'),
        ('OXXO', 'Oxxo voucher'),
        ('PP', 'PayPal'),
    ]
    payment = models.CharField(max_length=9,
                              choices=PAYMENT_CHOICES,
                              default="CC",
                              null=False,
                              blank=False)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total')
            )['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.lineitems.aggregate(
                Sum('lineitem_delivery')
                )['lineitem_delivery__sum'] or 0
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2,
                                         null=False, blank=False,
                                         editable=False)
    lineitem_delivery = models.DecimalField(max_digits=6, decimal_places=2,
                                         null=False, blank=False,
                                         editable=False, default=0)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        self.lineitem_delivery = self.product.shipping_cost * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'product number {self.product.id}' \
               f' on order {self.order.order_number}'


class PreOrder(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    upgraded_order = models.OneToOneField(Order, on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          default=None,
                                          related_name='preorder')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='preorders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(
        max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    county = models.CharField(
        max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    order_total = models.DecimalField(max_digits=10,
                                      decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)

    STATUS_CHOICES = [
        ('PEND', 'Pending'),
        ('INV', 'Invalid or experired'),
        ('UPG', 'Upgraded to order'),
    ]

    status = models.CharField(max_length=9,
                              choices=STATUS_CHOICES,
                              default="PEND",
                              null=False,
                              blank=False)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.lineitems.aggregate(
                Sum('lineitem_delivery')
                )['lineitem_delivery__sum'] or 0
        else:
            self.delivery_cost = 0
        self.total = self.order_total + self.delivery_cost
        self.grand_total = self.total * settings.PAY_PAL_DISCOUNT / 100
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class PreOrderLineItem(models.Model):
    order = models.ForeignKey(PreOrder, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    product = models.ForeignKey(Product, null=False,
                                blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_delivery = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2,
                                         null=False,
                                         blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        self.lineitem_delivery = self.product.shipping_cost * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'product number {self.product.id}' \
            'on order {self.order.order_number}'

class OxxoOrder(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    upgraded_order = models.OneToOneField(Order, on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          default=None,
                                          related_name='oxxoOrder')
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        default=''
        )
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='oxxoOrders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(
        max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    county = models.CharField(
        max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    order_total = models.DecimalField(max_digits=10,
                                      decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)

    STATUS_CHOICES = [
        ('PEND', 'Pending'),
        ('INV', 'Invalid or experired'),
        ('UPG', 'Upgraded to order'),
    ]

    status = models.CharField(max_length=9,
                              choices=STATUS_CHOICES,
                              default="PEND",
                              null=False,
                              blank=False)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.lineitems.aggregate(
                Sum('lineitem_delivery')
                )['lineitem_delivery__sum'] or 0
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OxxoOrderLineItem(models.Model):
    order = models.ForeignKey(OxxoOrder, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    product = models.ForeignKey(Product, null=False,
                                blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_delivery = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2,
                                         null=False,
                                         blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        self.lineitem_delivery = self.product.shipping_cost * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'product number {self.product.id}' \
            'on order {self.order.order_number}'

class Delivery(models.Model):
    tracking_number = models.CharField(max_length=32, null=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name='delivery'
        )
    provider = models.CharField(max_length=50, null=False, blank=False)
    expected_wait = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return self.tracking_number