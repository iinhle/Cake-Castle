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
