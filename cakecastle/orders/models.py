from django.db import models
from django.contrib.auth.models import User

class Cake(models.Model):
    name = models.CharField(max_length=255)
    flavor = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='cakes/', default='default_image.jpg')

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
    ]

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f'Order {self.id} by {self.customer_name}'

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='cake_images/', default='default_image.jpg')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Review(models.Model):
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.cake.name}'



