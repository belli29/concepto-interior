from django import template


register = template.Library()


@register.filter(name='calc_discount')
def calc_discount(price, discount):
    return float(price) * discount / 100
