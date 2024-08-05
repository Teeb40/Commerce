from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User,Bids,Placed,Comments,Wishlist
from django.shortcuts import render, get_object_or_404
import requests
from PIL import Image
import io 


def index(request):
    if request.method == 'POST':
        bid_amount = request.POST.get('bid')
        item_id = request.POST.get('item_id')
        username = request.POST.get('username')
        user = request.user
        
        # Ensure bid_amount is converted to the correct type if needed (e.g., float or decimal)
        try:
            bid_amount = float(bid_amount)
        except ValueError:
            return render(request, "auctions/error.html", {"error": "Invalid bid amount"})

        # Check if the bid already exists
        if Bids.objects.filter(item=item_id, username=username, amount=bid_amount).exists():
            return render(request, "auctions/error.html", {"error": "Bid Already Placed"})

        # Create a new bid
        current_bid = Bids.objects.create(item=item_id, amount=bid_amount, username=username)

        # Fetch the item and update its current bid
        item = get_object_or_404(Placed, id=item_id)
        item.current_bid = current_bid.amount
        item.save()  # Don't forget to save changes

        # Add the bid to the user's bids (assuming there's a many-to-many relationship)
        if hasattr(user, 'bids'):
            user.bids.add(current_bid)

    # Fetch all placed listings
    placed_listings = Placed.objects.all()
    return render(request, "auctions/index.html", {"listings": placed_listings})
    
    placed_listings = Placed.objects.all()
    return render(request, "auctions/index.html",{"listings":placed_listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        if request.method == 'POST':
                title = str(request.POST.get('title')).strip().title()
                description = str(request.POST.get('description')).strip()
                price = request.POST.get('price')
                category = request.POST.get('category')
                url = request.FILES.get('url')
                listings_ = Placed(title=title, description=description, price=price,category=category,url=url)
                if str(url).lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    print(title,description,price,category,url)
                else:
                    return render(request, "auctions/create_listing.html", {"not_filled": "Not a Valid Image File"})
                try:
                    listings_.full_clean()  
                    listings_.save()
                    return HttpResponseRedirect(reverse('index'))
                except ValidationError:
                    if len(description) > 100:
                        return render(request, "auctions/create_listing.html", {"not_filled": "Keep Description Below 100 Characters"})
                    elif len(title) > 20:
                        return render(request, "auctions/create_listing.html", {"not_filled": "Keep Name Below 64 Characters"})

                    return render(request, "auctions/create_listing.html", {"not_filled": "Fields Missing"})
        
        return render(request, "auctions/create_listing.html")
    
def listing(request, title,id):
    user = request.user
    username = request.user.username
    bid = Bids.objects.filter(item=id)
    id_ = id
    item = Placed.objects.get(id=id_)
    if item.current_bid:
        min_bid = item.current_bid + 0.01
    
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))


    info = Placed.objects.filter(title=title, id=id)
    if not info.exists():
        no_listing = "Page Not Found"
        return render(request, "auctions/listing.html", {"no_listing": no_listing})

   
    wishlist_item = None
    is_added = "Add to Wishlist"

    
    if request.method == 'POST':
        item_id = request.POST.get('wishlist')
        if item_id:
            item_id = int(item_id)  
            wishlist_item, created = Wishlist.objects.get_or_create(item_id=item_id, item_title=title)
            if user.wishlist.filter(id=wishlist_item.id).exists():
                user.wishlist.remove(wishlist_item)
                is_added = "Add to Watchlist"
                return HttpResponseRedirect(reverse("wishlist",args={f'{username}': username}))
            else:
                
                user.wishlist.add(wishlist_item)
                is_added = "Remove from Wishlist"
                return HttpResponseRedirect(reverse("wishlist",args={f'{username}': username}))
    else:
        
        wishlist_item = Wishlist.objects.filter(item_id=id, item_title=title).first()
        if wishlist_item and user.wishlist.filter(id=wishlist_item.id).exists():
            is_added = "Remove from Watchlist"
    if not item.current_bid:
        return render(request, "auctions/listing.html", {"listings": info, "is_added": is_added})
    else:
        return render(request, "auctions/listing.html", {"listings": info, "min_bid": min_bid,"is_added": is_added})

def wishlist(request,username):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    try:
        user_info = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "auctions/wishlist.html", {"error": "User Not Found"})

 
    if username != request.user.username:
        return render(request, "auctions/wishlist.html", {"error": "User Not Found"})


    wishlist_items = request.user.wishlist.all()

 
    wish_ids = wishlist_items.values_list('item_id', flat=True)

    
    products = Placed.objects.filter(id__in=wish_ids)

    return render(request, "auctions/wishlist.html", {"products": products})