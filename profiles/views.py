from django.shortcuts import render, get_object_or_404, redirect, reverse

from .models import UserProfile
from .forms import UserProfileForm
from checkout.models import Order, PreOrder
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Profile could not be updated!')
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all().order_by("-date")
    preorders = profile.preorders.all()
    preorders = preorders.exclude(status="INV").exclude(status="UPG").order_by("-date")
    template = 'profiles/profile.html'
    context = {
        'profile': profile,
        'orders': orders,
        'preorders': preorders,
        'form': form,
        'on_profile_page': True,
    }
    return render(request, template, context)
