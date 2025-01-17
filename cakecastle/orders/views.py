from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg
from .models import Cake, Order, Post, Review
from .forms import OrderForm, SignUpForm, PostForm, ReviewForm

def index(request):
    cakes = Cake.objects.all()
    posts = Post.objects.all()
    return render(request, 'orders/index.html', {'cakes': cakes, 'posts': posts})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'orders/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'orders/login.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='SiteOwner').exists())
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'orders/create_post.html', {'form': form})

@login_required
def submit_review(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.cake = cake
            review.user = request.user
            review.save()
            return redirect('cake_detail', cake_id=cake.id)
    else:
        form = ReviewForm()
    return render(request, 'orders/submit_review.html', {'form': form, 'cake': cake})

def cake_detail(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    reviews = cake.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    return render(request, 'orders/cake_detail.html', {'cake': cake, 'reviews': reviews, 'avg_rating': avg_rating})

from django.core.mail import send_mail
from django.conf import settings

def update_order_status(order, status):
    order.status = status
    order.save()
    send_mail(
        'Order Status Update',
        f'Your order for {order.cake.name} is now {order.get_status_display()}.',
        settings.EMAIL_HOST_USER,
        [order.user.email],
        fail_silently=False,
    )

import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': order.cake.name,
                },
                'unit_amount': int(order.cake.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )
    return redirect(session.url, code=303)

import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

@login_required
def create_paypal_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/paypal-success/'),
            "cancel_url": request.build_absolute_uri('/paypal-cancel/')
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": order.cake.name,
                    "sku": str(order.id),  # Ensure sku matches order.id for success view
                    "price": str(order.cake.price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(order.cake.price),
                "currency": "USD"
            },
            "description": f"Order for {order.cake.name}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        return render(request, 'orders/payment_error.html', {'error': payment.error})

@login_required
def paypal_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Update order status to "Paid" or equivalent
        order = get_object_or_404(Order, id=payment.transactions[0].item_list.items[0].sku)
        order.status = 'Paid'
        order.save()
        return render(request, 'orders/payment_success.html')
    else:
        return render(request, 'orders/payment_error.html', {'error': payment.error})

@login_required
def paypal_cancel(request):
    return render(request, 'orders/payment_cancel.html')

def success(request):
    return render(request, 'orders/success.html')

def cancel(request):
    return render(request, 'orders/cancel.html')

from django.shortcuts import render

def track_order(request):
    return render(request, 'orders/track_order.html')

from django.shortcuts import render, get_object_or_404
from .models import Order

def track_order(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'orders/track_order.html', {'order': order})
