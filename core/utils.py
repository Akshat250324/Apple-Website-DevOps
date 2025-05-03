# utils.py
from .models import Cart
from django.shortcuts import render

def get_cart_count(user):
    if user.is_authenticated:
        return Cart.objects.filter(user=user).count()
    return 0

def render_with_cart(request, template_name, context=None):
    if context is None:
        context = {}
    context['cart_count'] = get_cart_count(request.user)
    return render(request, template_name, context)
