from django.shortcuts import render

# Creating views

from django.shortcuts import render
from .models import Cake, Order

def index(request):
    cakes = Cake.objects.all()
    return render(request, 'orders/index.html', {'cakes': cakes})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

