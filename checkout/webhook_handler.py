from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Order, OrderLineItem, OxxoOrder, OxxoOrderLineItem
from products.models import Product
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from profiles.models import UserProfile
import json
import time

breakpoint
class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )
    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded_or_requires_action(self, event):
        """
        Handle the payment_intent.succeeded and payment_intent.requires_action webhook from Stripe
        """
        if event.type == 'payment_intent.requires_action':
            payment_confirmed = False
        else:
            payment_confirmed = True
        # fetching relevant Stripe event details
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info
        if payment_confirmed:
            billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        if payment_confirmed:
            grand_total = round((intent.charges.data[0].amount / 100), 2)
        else:
            grand_total = round((intent.amount / 100), 2)
        # if payment confirmation for oxxo payment
        if payment_confirmed and intent.payment_method_details.type == 'oxxo':
            oxxo_order = OxxoOrder.objects.get(
                stripe_pid=pid
                )
            # update oxxo order status
            oxxo_order.status = 'UPG'
            oxxo_order.save()
            # create new order connected
            order = Order(
                    user_profile=oxxo_order.user_profile,
                    full_name=oxxo_order.full_name,
                    email=oxxo_order.email,
                    phone_number=oxxo_order.phone_number,
                    country=oxxo_order.country,
                    postcode=oxxo_order.postcode,
                    town_or_city=oxxo_order.town_or_city,
                    street_address1=oxxo_order.street_address1,
                    street_address2=oxxo_order.street_address2,
                    county=oxxo_order.county,
                    delivery_cost=oxxo_order.delivery_cost,
                    order_total=oxxo_order.order_total,
                    grand_total=oxxo_order.grand_total,
                    oxxo=True
                )
            order.save()
            # copy line items from oxxo order to order
            for li in oxxo_order.lineitems.all():
                oxxo_order_line_item = OxxoOrderLineItem(
                    order=order,
                    product=li.product,
                    quantity=li.quantity,
                )
                oxxo_order_line_item .save()
            # update product reserved, sold
            product = li.product
            quantity = li.quantity
            product.sold = product.sold + quantity
            product.reserved = product.reserved - quantity
            product.save()
            return HttpResponse(
                content=f'Webhook received: {event["type"]}'
                ' | SUCCESS: Oxxo Order paid by customer',
                status=200
                )
        # clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # update available quantity and sold quantity of products
        bag_dict = json.loads(bag)
        for p, quantity in bag_dict.items():
            print(quantity)
            product = get_object_or_404(Product, pk=p)
            print(product.available_quantity)
            print(product.reserved)
            if payment_confirmed:
                product.sold = product.sold + quantity
            else:
                product.reserved = product.reserved + quantity
            product.available_quantity = product.available_quantity - quantity
            product.save()

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = (
                    shipping_details.address.postal_code
                )
                profile.default_town_or_city = (
                    shipping_details.address.city
                )
                profile.default_street_address1 = (
                    shipping_details.address.line1
                )
                profile.default_street_address2 = (
                    shipping_details.address.line2
                )
                profile.default_county = (
                    shipping_details.address.state
                )
                profile.save()
        # check if order exist
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                if payment_confirmed:
                    order = Order.objects.get(
                        stripe_pid=pid,
                    )
                else:
                    order = OxxoOrder.objects.get(
                        stripe_pid=pid
                    )
                order_exists = True
                break
            except OxxoOrder.DoesNotExist:
                attempt += 1
                time.sleep(1)
        # order exists
        if order_exists:
            print("order exists!")
            if payment_confirmed:
                self._send_confirmation_email(order)
                return HttpResponse(
                    content=f'Webhook received: {event["type"]}'
                    ' | SUCCESS: Verified order already in database',
                    status=200
                    )
            else:
                return HttpResponse(
                    content=f'Webhook received: {event["type"]}'
                    ' | SUCCESS: Verified Oxxo order already in database',
                    status=200
                    )

        # order does not exists
        else:
            order = None
            try:
                if payment_confirmed:
                    order = Order.objects.create(
                        full_name=shipping_details.name,
                        user_profile=profile,
                        email=billing_details.email,
                        phone_number=shipping_details.phone,
                        country=shipping_details.address.country,
                        postcode=shipping_details.address.postal_code,
                        town_or_city=shipping_details.address.city,
                        street_address1=shipping_details.address.line1,
                        street_address2=shipping_details.address.line2,
                        county=shipping_details.address.state,
                        original_bag=bag,
                        stripe_pid=pid,
                    )
                    for item_id, item_data in json.loads(bag).items():
                        product = Product.objects.get(id=item_id)
                        order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                        order_line_item.save()
                else:
                    order = OxxoOrder.objects.create(
                        full_name=shipping_details.name,
                        user_profile=profile,
                        email=intent.receipt_email,
                        phone_number=shipping_details.phone,
                        country=shipping_details.address.country,
                        postcode=shipping_details.address.postal_code,
                        town_or_city=shipping_details.address.city,
                        street_address1=shipping_details.address.line1,
                        street_address2=shipping_details.address.line2,
                        county=shipping_details.address.state,
                        original_bag=bag,
                        stripe_pid=pid,
                    )
                    for item_id, item_data in json.loads(bag).items():
                        product = Product.objects.get(id=item_id)
                        order_line_item = OxxoOrderLineItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                        order_line_item.save()

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]}'
                ' | SUCCESS: Created order in webhook',
                status=200
                )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)