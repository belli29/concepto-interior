from django.shortcuts import render, redirect, reverse
from django.shortcuts import get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .forms import OrderForm, PreOrderForm, OxxoOrderForm
from .models import Order, OrderLineItem, PreOrder, PreOrderLineItem, OxxoOrder, OxxoOrderLineItem
from products.models import Product
from bag.contexts import bag_contents
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
import stripe
import json
import time


def checkout(request):
    """
    render checkout page and does not allow checkout
    in case of delivery issue,
    handle POST requests (Stripe and PayPal)
    """
    if request.method == 'POST':
        payment_choice = request.POST['payment-choice']
        bag = request.session.get('bag', {})
        # collect data from the form
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': 'MX',
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # stripe
        if payment_choice == "stripe" or payment_choice == "oxxo":
            # validate form
            if payment_choice == "stripe":
                order_form = OrderForm(form_data)
            else:
                order_form = OxxoOrderForm(form_data)
            if order_form.is_valid():
                pid = request.POST.get('client_secret').split('_secret')[0]
                #avoid order duplication if user does leave the oxxo voucher modal open for too long
                if payment_choice == "oxxo":
                    attempt = 1
                    while attempt <= 10:
                        try:
                            # order already created by Webhook
                            order = OxxoOrder.objects.get(stripe_pid=pid)
                            break
                        except OxxoOrder.DoesNotExist:
                            attempt += 1
                            time.sleep(1)
                            if attempt == 10:
                                order = order_form.save()
                                # add pid and original bag to order
                                order.stripe_pid = pid
                                order.original_bag = json.dumps(bag)
                else:
                    order = order_form.save()
                    # add pid and original bag to order
                    order.stripe_pid = pid
                    order.original_bag = json.dumps(bag)
                # add line items to order
                for item_id, item_quantity in bag.items():
                    try:
                        product = Product.objects.get(id=item_id)
                        if payment_choice == "stripe":
                            order_line_item = OrderLineItem(
                                        order=order,
                                        product=product,
                                        quantity=item_quantity,
                                    )
                        else:
                            order_line_item = OxxoOrderLineItem(
                                        order=order,
                                        product=product,
                                        quantity=item_quantity,
                                    )
                        order_line_item.save()
                    except Product.DoesNotExist:
                        messages.error(request, (
                            "One of the products in your bag"
                            "wasn't found in our database. "
                            "Contact us for assistance!")
                        )
                        order.delete()
                        return redirect(reverse('view_bag'))
            else:
                messages.error(request, 'There was an error with your form. \
                    Please double check your information.')
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[payment_choice, order.order_number])
            )
        # paypal
        if payment_choice == 'paypal':
            # validate form
            pre_order_form = PreOrderForm(form_data)
            if pre_order_form.is_valid():
                pre_order = pre_order_form.save()
                # add line items to preorder
                for item_id, item_quantity in bag.items():
                    try:
                        product = Product.objects.get(id=item_id)
                        pre_order_line_item = PreOrderLineItem(
                                    order=pre_order,
                                    product=product,
                                    quantity=item_quantity,
                                )
                        pre_order_line_item.save()
                    except Product.DoesNotExist:
                        messages.error(request, (
                            "One of the products in your bag"
                            "wasn't found in our database."
                            "Contact us for assistance!")
                        )
                        pre_order.delete()
                        return redirect(reverse('view_bag'))
            else:
                messages.error(request, 'There was an error with your form. \
                Please double check your information.')
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse(
                'invoice_confirmation', args=[pre_order.order_number])
                )

    # GET request
    else:
        context = bag_contents(request)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag")
            return redirect(reverse('products'))
        current_bag = bag_contents(request)
        grand_total = current_bag['grand_total']

        # Stripe intent
        stripe_total = round(grand_total*100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            payment_method_types=['card', 'oxxo']
        )
        client_secret = intent.client_secret
        # generate form
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret':  client_secret
            }
        return render(request, template, context)


def checkout_success(request, order_number, payment_method):
    """
    Handle successful checkouts for
    Stripe orders or Oxxo orders
    """
    save_info = request.session.get('save_info')
    if payment_method == "stripe":
        order = get_object_or_404(Order, order_number=order_number)
        messages.success(request, f'Compra confirmada!\
        Te hemos mandado la confirmacion a  {order.email}.')
    else:
        order = get_object_or_404(OxxoOrder, order_number=order_number)
        messages.success(request, f'Te hemos mandado las instrucciones por el pago a  {order.email}.')

    # Attach the user's profile to the order if user is authenticated
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()
    # save info if user has checked save-info box
    if save_info:
        profile_data = {
            'default_phone_number': order.phone_number,
            'default_country': order.country,
            'default_postcode': order.postcode,
            'default_town_or_city': order.town_or_city,
            'default_street_address1': order.street_address1,
            'default_street_address2': order.street_address2,
            'default_county': order.county,
        }
        user_profile_form = UserProfileForm(profile_data, instance=profile)
        if user_profile_form.is_valid():
            user_profile_form.save()

    # save session bag info to a bag variable
    bag = request.session['bag']
    bag_with_item_name = []
    for key, value in bag.items():
        product = get_object_or_404(Product, pk=key)
        bag_with_item_name.append({
            'name': product.name,
            'quantity': value

        })
    # deletes session bag
    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'bag': bag_with_item_name,
        'payment': payment_method
    }

    return render(request, template, context)


@require_POST
def cache_checkout_data(request):
    """
    Add metadata to stripe payment intent
    """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, "There was something wrong with your payment.\
            Please try later")
        return HttpResponse(status=400)




def invoice_confirmation(request, pre_order_number):
    """
    Handle invoice confirmation when user selects paypal payment method
    """
    order = get_object_or_404(PreOrder, order_number=pre_order_number)

    send_email_seller(order, 'preorder')
    # send email
    cust_email = order.email
    subject = render_to_string(
        'checkout/confirmation_emails/confirmation_email_subject.txt',
        {'order': order})
    body = render_to_string(
        'checkout/confirmation_emails/confirmation_email_body.txt',
        {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL, 'action': 'preorder'})
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [cust_email]
    )

    # update available quantity and reserved quantity of products
    for p, quantity_reserved in request.session['bag'].items():
        product = get_object_or_404(Product, pk=p)
        initial_quantity = product.available_quantity
        initial_reserved = product.reserved
        reserved = initial_reserved + quantity_reserved
        available_quantity = initial_quantity - quantity_reserved
        product.available_quantity = available_quantity
        product.reserved = reserved
        product.save()

    # Attach the user's profile to the pre order if user is authenticated
    profile = None
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()
        # save info if user has checked save-info box
        if request.session['save_info']:
            username = request.user.username
            profile = UserProfile.objects.get(user__username=username)
            profile.default_phone_number = order.phone_number
            profile.default_country = order.country
            profile.default_postcode = order.postcode
            profile.default_town_or_city = order.town_or_city
            profile.default_street_address1 = order.street_address1
            profile.default_street_address2 = order.street_address2
            profile.default_county = order.county
            profile.save()

    # delete session bag
    if 'bag' in request.session:
        del request.session['bag']

    # add success message
    messages.success(
        request, f'Pronto recibiras la factura a {cust_email}.'
    )

    template = 'checkout/invoice_confirmation.html'
    context = {
        "order": order,
    }
    return render(request, template, context)


def delete_session_chosen_country(request):

    del request.session['chosen_country']
    return HttpResponse(status=200)


def quantity_problem(request):
    """Check if the quantity of the items does not
    exceed the quantity available"""
    quantity_problem = False
    bag = request.session.get('bag', {})
    for item_id, item_quantity in bag.items():
        product = Product.objects.get(id=item_id)
        if item_quantity >= product.available_quantity:
            quantity_problem = True
            break
    if not quantity_problem:
        # OK Stripe Payment and order creation can go ahead
        return HttpResponse(status=200)

    else:
        messages.error(request, "Oops ... there was a problem ")
        del request.session['bag']
        return redirect(reverse('products'))

# helper functions
def send_email_seller(order, action):
    """Send the seller a confirmation email"""
    seller_email = settings.SELLER_EMAIL
    subject = render_to_string(
        'checkout/confirmation_emails/seller_email_subject.txt',
        {'order': order})
    body = render_to_string(
        'checkout/confirmation_emails/seller_email_body.txt',
        {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL, 'action': action})

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [seller_email]
    )