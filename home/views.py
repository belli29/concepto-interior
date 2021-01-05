from django.shortcuts import render, redirect, reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages


def index(request):
    """returns index page"""

    return render(request, 'home/index.html')


def contact(request):
    """returns contact page"""

    return render(request, 'home/contact.html')


def about(request):
    """returns about page"""

    return render(request, 'home/about.html')


def support(request):
    """returns support page"""
    if request.method == 'POST':
        problem = request.POST.get('problem')
        # send email
        subject = render_to_string(
            'checkout/confirmation_emails/support_email_subject.txt',
            )
        body = render_to_string(
            'checkout/confirmation_emails/support_email_body.txt',
            {'problem': problem, })

        send_mail(
            subject,
            body,
            None,
            [settings.IT_SUPPORT_EMAIL]
        )
        messages.success(request, "Thanks for contacting me.\
        I'll check the issue and let you know as soon as possible")
        return redirect(reverse('home'))
    return render(request, 'home/support.html')
