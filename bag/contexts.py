from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from checkout.models import Order, PreOrder, OxxoOrder
from django.utils import timezone
from django.utils.timezone import localdate


def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    shipping_cost = 0
    bag = request.session.get('bag', {})
    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        subtotal = quantity * product.price
        total += subtotal
        shipping_cost += product.shipping_cost * quantity
        product_count += quantity
        remaining_qty = product.available_quantity - quantity
        """
        creates a list with number of avaialable items
        """
        available_quantity_list = []
        n = 1
        while n <= product.available_quantity:
            available_quantity_list.append(n)
            n += 1

        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'remaining_qty': remaining_qty,
            'product': product,
            'total': subtotal,
            'available_quantity_list': available_quantity_list,
        })

    delivery = shipping_cost
    free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    grand_total =  total + shipping_cost

    # for seller banner
    today = timezone.now().replace(hour=0, minute=0, second=0)
    today_orders = Order.objects.all().filter(
        date__gte=today)
    today_preorders = PreOrder.objects.all().filter(
        date__gte=today)
    today_oxxo_orders = OxxoOrder.objects.all().filter(
        date__gte=today)
    today_orders_count = len(today_orders)
    today_preorders_count = len(today_preorders)
    today_oxxo_orders_count = len(today_oxxo_orders)

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': grand_total,
        'discount': settings.PAY_PAL_DISCOUNT,
        'today': today,
        'today_orders_count': today_orders_count,
        'today_preorders_count': today_preorders_count,
        'today_oxxo_orders_count': today_oxxo_orders_count,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
    }

    return context