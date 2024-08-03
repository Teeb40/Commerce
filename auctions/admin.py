from django.contrib import admin
from .models import Bids,Placed,Comments,User,Wishlist
# Register your models here.
admin.site.register(Comments)
admin.site.register(Placed)
admin.site.register(User)
admin.site.register(Bids)
admin.site.register(Wishlist)