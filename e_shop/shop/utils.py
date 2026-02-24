import json
import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def generate_sslcommerz_payment(order, request):
    post_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': float(order.get_total_cost()),
        'currency': 'BDT',
        'tran_id': str(order.id),
        'success_url': request.build_absolute_uri(f'/payment/success/{order.id}/'),
        'fail_url': request.build_absolute_uri(f'/payment/fail/{order.id}/'),
        'cancel_url': request.build_absolute_uri(f'/payment/cancel/{order.id}/'),
        'cus_name':f"{order.first_name} {order.last_name}",
        'cus_email': order.email,
        'cus_add1': order.address,
        'cus_city': order.city,
        'cus_postcode': order.postal_code,
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': 'products from our store',
        'product_category': 'General',
        'product_profile': 'general',
    }
    
    response = requests.post(settings.SSLCOMMERZ_API_URL, data=post_data)
    return response.json()

def send_confirmation_email(order):
    subject = f'Order Confirmation - Order #{order.id}'
    html_message = render_to_string('shop/email/order_confirmation.html', {'order': order})
    from django.core.mail import send_mail
    send_mail(
        subject,
        f'Thank you for your order #{order.id}',
        settings.EMAIL_HOST_USER,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )