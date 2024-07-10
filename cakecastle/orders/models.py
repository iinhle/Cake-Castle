from django.db import models

# Create your models here.

from django.db import models

class Cake(models.Model):
    name = models.CharField(max_length=255)
    flavor = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='cakes/')

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)

