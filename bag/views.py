from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


def bag(request):
    """returns bag page"""
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
        messages.success(
            request, f'Updated {product.name} quantity to {bag[item_id]}'
        )
    else:
        bag[item_id] = quantity
        messages.success(request, f'Added {product.name} to your bag')
    request.session['bag'] = bag
    return redirect(redirect_url)


def update_bag(request, item_id):
    """ amend the amount of a specific item in the bag"""
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    bag = request.session.get('bag', {})
    bag[item_id] = quantity
    request.session['bag'] = bag
    messages.success(
        request, f'Updated {product.name} quantity to {bag[item_id]}'
    )
    return redirect("view_bag")


def remove_from_bag(request, item_id):
    """ Remove a specific product from the shopping bag """
    product = get_object_or_404(Product, pk=item_id)
    bag = request.session.get('bag', {})
    try:
        del bag[item_id]
        request.session['bag'] = bag
        messages.success(request, f'Removed {product.name} from the bag')
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, f'Error removing item:{e}')
        return HttpResponse(status=500)
