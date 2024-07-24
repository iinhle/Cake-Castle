from django.contrib import admin

# models

from django.contrib import admin
from .models import Cake, Order, Post

admin.site.register(Cake)
admin.site.register(Order)
admin.site.register(Post)
