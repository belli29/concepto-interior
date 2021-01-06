from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey('Category', null=True,
                                 blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    description = models.TextField()
    available_quantity = models.PositiveIntegerField(default=20)
    sold = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
        )
    image_one = models.ImageField(null=True, blank=True)
    image_two = models.ImageField(null=True, blank=True)
    image_three = models.ImageField(null=True, blank=True)
    l = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(999)]
        )
    h = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(999)]
        )
    w = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(999)]
        )
    shipping_cost = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(99999)]
        )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
