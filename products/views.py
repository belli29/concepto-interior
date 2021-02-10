from django.shortcuts import render, get_object_or_404, HttpResponse
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Product, Category
from .forms import ProductForm
from checkout.models import Order, OrderLineItem, PreOrder, OxxoOrder, Delivery
from checkout.forms import DeliveryForm


def all_products(request):
    """view showing all products, including sorting and search queried"""
    # save current parameters in a variable
    current_url = request.get_full_path()
    if '?' in current_url:
        current_param = current_url.split('?')[1]
    else:
        current_param = ""

    products = Product.objects.filter(is_active=True)
    products = products.order_by("price")
    query = None
    category = None
    sort = None
    direction = None
    available_filter = False

    if 'available_filter' in request.GET:
        products = products.filter(available_quantity__gt=0)
        available_filter = True
    # filter results
    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkey
        if sortkey == 'size':
            products = products.annotate(size=F('l')*F('w')*F('h'))
        if 'direction' in request.GET:
            direction = request.GET['direction']
            if direction == 'desc':
                sortkey = f'-{sortkey}'
        products = products.order_by(sortkey)

    if 'q' in request.GET:
        query = request.GET['q']
        if not query:
            messages.error(request, 'You have not entered any search criteria')
            return redirect(reverse('products'))

        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    if 'category' in request.GET:
        category = request.GET['category']
        products = products.filter(category__name=category)
        category = Category.objects.filter(name=category)[0]

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_category': category,
        'current_sorting': current_sorting,
        'available_filter_active': available_filter,
        'current_param': current_param
    }

    return render(request, 'products/products.html', context)


def product_details(request, product_id):
    """view showing details of the selected product"""

    product = get_object_or_404(Product, pk=product_id)
    bag_qty = 0
    if 'bag' in list(request.session.keys()):
        if str(product_id) in list(request.session.get("bag").keys()):
            bag_qty = request.session.get("bag")[str(product_id)]
    remaining_qty = product.available_quantity - bag_qty
    shipping_cost = product.shipping_cost
    context = {
        'product': product,
        'remaining_qty': remaining_qty,
        'shipping_cost': shipping_cost
    }

    return render(request, 'products/product_details.html', context)


"""Products management view"""


@login_required
def management(request):
    """view allowing super users to manage inventory """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    # orders section
    delivery_form = DeliveryForm()
    orders = Order.objects.all().order_by("-date")
    preorders = PreOrder.objects.all()
    preorders = preorders.exclude(status="INV").exclude(status="UPG")
    preorders = preorders.order_by("-date")
    oxxo_orders = OxxoOrder.objects.all().order_by("-date")
    pay_pal_filter = False
    shipped_filter = False
    unshipped_filter = False
    view_preorders = False
    sort = None
    direction = None
    if 'view_preorders' in request.GET:
        view_preorders = True
    if 'pay_pal_filter' in request.GET:
        orders = orders.exclude(pp_transaction_id="")
        pay_pal_filter = True
    if 'shipped_filter' in request.GET:
        orders = orders.filter(shipped=True)
        shipped_filter = True
    if'unshipped_filter' in request.GET:
        orders = orders.filter(shipped=False)
        unshipped_filter = True
    # save current parameters in a variable
    current_url = request.get_full_path()
    if '?' in current_url:
        current_param = current_url.split('?')[1]
    else:
        current_param = ""
    # filter results
    if 'sort' in request.GET:
        sort = request.GET['sort']
        sortkey = request.GET['sort']
        if 'direction' in request.GET:
            direction = request.GET['direction']
            if direction == 'desc':
                sortkey = f'-{sortkey}'
        orders = orders.order_by(sortkey)
        preorders = preorders.order_by(sortkey)
        oxxo_orders = oxxo_orders.order_by(sortkey)
    current_sorting = f'{sort}-{direction}'
    context = {
        'view_preorders': view_preorders,
        'orders': orders,
        'preorders': preorders,
        'oxxo_orders': oxxo_orders,
        'pay_pal_filter_active': pay_pal_filter,
        'shipped_filter_active': shipped_filter,
        'unshipped_filter_active': unshipped_filter,
        'current_param': current_param,
        'current_sorting': current_sorting,
        'delivery_form': delivery_form
    }
    template = 'products/management.html'
    return render(request, template, context)


@login_required
def add_product(request):
    """view adding a new product """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'You succesfully added a product!')
            # identify if the user was coming from management dashboard
            from_management = request.POST['from_management']
            if from_management:
                return redirect(reverse('list_products'))
            else:
                return redirect(reverse("product_details", args=[product.id]))
        else:
            messages.error(
               request,
               'Something went wrong. We could not add the product.'
               )

    else:
        form = ProductForm()
    # define if the user is coming from management dashboard
    from_management = request.GET.get("from_management", False)
    context = {
        "form": form,
        "from_management": from_management,
    }
    template = 'products/add_product.html'
    return render(request, template, context)


@login_required
def list_products(request):
    """view listing all products """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    all_products = Product.objects.all()
    context = {
            "products": all_products,
        }
    template = 'products/list_products.html'
    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            # identify if the user was coming from management dashboard
            from_management = request.POST['from_management']
            if from_management:
                return redirect(reverse('list_products'))
            else:
                return redirect(reverse('product_details', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.'
                )
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')
    template = 'products/edit_product.html'
    # define if the user is coming from management dashboard
    from_management = request.GET.get("from_management", False)
    context = {
        'form': form,
        'product': product,
        'from_management': from_management,
    }
    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, f'Product {product.name} deleted!')
    return redirect(reverse('list_products'))


@login_required
def toggle_active(request, product_id):
    """ Toggle a product is_active field """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    if product.is_active:
        product.is_active = False
        product.save()
    else:
        product.is_active = True
        product.save()
    return redirect(reverse('list_products'))


@login_required
def confirm_pre_order(request, order_number):
    """ view upgrading preorder and creating a corresponding order """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can see that.')
        return redirect(reverse('home'))
    pre_order = get_object_or_404(PreOrder, order_number=order_number)
    pp_transaction_id = request.POST['pp_transaction_id']
    order = Order(
        user_profile=pre_order.user_profile,
        full_name=pre_order.full_name,
        email=pre_order.email,
        phone_number=pre_order.phone_number,
        country=pre_order.country,
        postcode=pre_order.postcode,
        town_or_city=pre_order.town_or_city,
        street_address1=pre_order.street_address1,
        street_address2=pre_order.street_address2,
        county=pre_order.county,
        delivery_cost=pre_order.delivery_cost,
        order_total=pre_order.order_total,
        grand_total=pre_order.grand_total,
        pp_transaction_id=pp_transaction_id
    )
    # save order
    order.save()
    # copy line items from preorder to order
    for li in pre_order.lineitems.all():
        order_line_item = OrderLineItem(
            order=order,
            product=li.product,
            quantity=li.quantity,
        )
        order_line_item.save()
        # update product reserved, sold
        product = li.product
        quantity = li.quantity
        product.sold = product.sold + quantity
        product.reserved = product.reserved - quantity
        product.save()
    # update preorder
    pre_order.upgraded_order = order
    pre_order.status = "UPG"
    pre_order.save()
    # success message
    messages.success(request, (
        f'Preorder {pre_order.order_number} upgraded.'
        f'New order {order.order_number} confirmed.'
        )
    )
    return redirect(reverse('products_management'))


@login_required
def invalid_pre_order(request, order_number):
    """ view amending preorder to invalid or expired """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can see that.')
        return redirect(reverse('home'))
    pre_order = get_object_or_404(PreOrder, order_number=order_number)
    # update product avaiable, reserved
    for li in pre_order.lineitems.all():
        product = li.product
        quantity = li.quantity
        product.available_quantity = product.available_quantity + quantity
        product.reserved = product.reserved - quantity
        product.save()

    # email user
    cust_email = pre_order.email
    subject = render_to_string(
        'checkout/confirmation_emails/invalid_preorder_subject.txt',
        {'preorder': pre_order})
    body = render_to_string(
        'checkout/confirmation_emails/invalid_preorder_body.txt',
        {'preorder': pre_order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [cust_email]
    )
    # delete preorder
    pre_order.status = "INV"
    pre_order.save()
    # success message
    messages.success(
        request,
        f'preorder {pre_order.order_number} marked as invalid or expired.'
        'Avaialbility has been replenished'
        )
    return redirect(reverse('products_management'))


@login_required
def toggle_shipped(request, order_id):
    """ Toggle a product shipped field,
    create /delete delivery instance,
    amend order instance
    and inform user by email """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    order = get_object_or_404(Order, pk=order_id)
    # amend order as shipped
    if not order.shipped:
        order.shipped = True
        order.save()
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = Delivery(
                tracking_number=request.POST['tracking_number'],
                provider=request.POST['provider'],
                expected_wait=request.POST['expected_wait'],
                order=order
            )
            delivery.save()
            messages.success(
                request,
                f"Order {order.order_number} confirmed as shipped!\n"
                f"Delivery {delivery.tracking_number} by {delivery.provider}"
                ' has been created.'
                )
            # send email to customer
            cust_email = order.email
            subject = render_to_string(
                'checkout/confirmation_emails/order_shipped_subject.txt',
                {'order': order}
                )
            body = render_to_string(
                'checkout/confirmation_emails/order_shipped_body.txt',
                {'order': order,
                 'contact_email': settings.DEFAULT_FROM_EMAIL,
                 'delivery': delivery
                 }
                )
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [cust_email]
            )
        else:
            messages.error(
                request,
                'Something went wrong. Delivery cannnot be added.'
            )
    # amend order as not shipped
    else:
        order.shipped = False
        order.save()
        try:
            delivery = get_object_or_404(Delivery, order=order)
            delivery.delete()
        except:
            pass
        messages.success(
            request, 'customer has been informed there was an error:'
            ' order has not been shipped yet. '
            f'Any delivery associated to order {order.order_number}'
            ' has been deleted'
        )
        # email customer :order was marked as shipped by mistake
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/order_not_shipped_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/order_not_shipped_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )
    return redirect(reverse('products_management'))
