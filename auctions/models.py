from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator,MinLengthValidator
from django.utils import timezone

class Wishlist(models.Model):
        item_id = models.IntegerField()
        item_title = models.CharField(max_length=100)
        def __str__(self):
             return f"{self.item_id}"
class Bids(models.Model):
    item = models.IntegerField(default=0)
    amount = models.FloatField(default=0)
    name = models.CharField(max_length=100)
    def __str__(self):
         return f"{self.amount}"
    
class User(AbstractUser):
    wishlist = models.ManyToManyField(Wishlist,blank=True,related_name="items")
    bids = models.ManyToManyField(Bids,blank=True,related_name="bid")
    winning_bids = models.ManyToManyField(Bids,blank=True,related_name="winning_bid")

    def __str__(self):
         return f"Username:{self.username} Email: {self.email} winnings: {self.winning_bids}"



class Placed(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=20, validators=[MinLengthValidator(1)])
    description = models.CharField(max_length=100,validators=[MinLengthValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(1.00)])
    category = models.CharField(max_length=100,validators=[MinLengthValidator(1)])
    url = models.ImageField(upload_to='images/', blank=True, default='No Image')  
    created_at = models.DateTimeField(auto_now_add=True)
    current_bid = models.FloatField(blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title}"


    




class Comments(models.Model):
    ...
