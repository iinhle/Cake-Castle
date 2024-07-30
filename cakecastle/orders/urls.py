from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_list/', views.order_list, name='order_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('create_post/', views.create_post, name='create_post'),
    path('order/<int:order_id>/checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('order/<int:order_id>/paypal/', views.create_paypal_payment, name='create_paypal_payment'),
    path('paypal-success/', views.paypal_success, name='paypal_success'),
    path('paypal-cancel/', views.paypal_cancel, name='paypal_cancel'),
    path('track_order/<int:order_id>/', views.track_order, name='track_order'), 
]
