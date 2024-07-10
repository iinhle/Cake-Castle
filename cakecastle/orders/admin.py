from django.contrib import admin

# models

from django.contrib import admin
from .models import Cake, Order

admin.site.register(Cake)
admin.site.register(Order)

