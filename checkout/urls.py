from django.urls import path
from . import views
from .webhooks import webhook
urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
    path('wh/', webhook, name='webhook'),
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
    path('invoice_confirmation/<pre_order_number>', views.invoice_confirmation, name='invoice_confirmation'),
    path('delete_session_chosen_country', views.delete_session_chosen_country, name='delete_session_chosen_country'),
    path('quantity_problem', views.quantity_problem, name='quantity_problem'),
]