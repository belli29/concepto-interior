from django.contrib import admin
from .models import Order, OrderLineItem
from .models import PreOrder, PreOrderLineItem
from .models import Delivery


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag', 'stripe_pid',
                       'pp_transaction_id')

    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag',
              'stripe_pid', "shipped",
              "pp_transaction_id")

    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total', "shipped")

    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)


# preorder
class PreOrderLineItemAdminInline(admin.TabularInline):
    model = PreOrderLineItem
    readonly_fields = ('lineitem_total',)


class PreOrderAdmin(admin.ModelAdmin):
    inlines = (PreOrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'upgraded_order')

    fields = ('order_number', 'upgraded_order', 'status',
              'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total',)

    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total', 'status',)

    ordering = ('-date',)


admin.site.register(PreOrder, PreOrderAdmin)

# delivery


class DeliveryAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

    fields = ('order',
              'tracking_number',
              'provider',
              'expected_wait'
              )

    list_display = ('order', 'tracking_number')

    ordering = ('-date',)

admin.site.register(Delivery, DeliveryAdmin)