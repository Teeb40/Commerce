from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User,Bids,Placed,Comments,Wishlist
import requests
from PIL import Image
import io 


def index(request):
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
    # Redirect to login if user is not authenticated
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # Fetch the listing info
    info = Placed.objects.filter(title=title, id=id)
    if not info.exists():
        no_listing = "Page Not Found"
        return render(request, "auctions/listing.html", {"no_listing": no_listing})

    # Initialize variables
    wishlist_item = None
    is_added = "Add to Wishlist"

    # Handle POST request
    if request.method == 'POST':
        item_id = request.POST.get('wishlist')
        if item_id:
            item_id = int(item_id)  # Ensure item_id is an integer
            wishlist_item, created = Wishlist.objects.get_or_create(item_id=item_id, item_title=title)
            if user.wishlist.filter(id=wishlist_item.id).exists():
                # Remove the item from the wishlist
                user.wishlist.remove(wishlist_item)
                is_added = "Add to Watchlist"
                return HttpResponseRedirect(reverse("wishlist",args={f'{username}': username}))
            else:
                # Add the item to the wishlist
                user.wishlist.add(wishlist_item)
                is_added = "Remove from Wishlist"
                return HttpResponseRedirect(reverse("wishlist",args={f'{username}': username}))
    else:
        # For GET request, check if the item is already in the wishlist
        wishlist_item = Wishlist.objects.filter(item_id=id, item_title=title).first()
        if wishlist_item and user.wishlist.filter(id=wishlist_item.id).exists():
            is_added = "Remove from Watchlist"

    return render(request, "auctions/listing.html", {"listings": info, "is_added": is_added})

def wishlist(request,username):
    # Redirect to login if user is not authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # Fetch the user info
    try:
        user_info = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "auctions/wishlist.html", {"error": "User Not Found"})

    # Check if the username in the URL matches the signed-in user
    if username != request.user.username:
        return render(request, "auctions/wishlist.html", {"error": "User Not Found"})

    # Fetch wishlist items for the user
    wishlist_items = request.user.wishlist.all()

    # Extract the IDs from the wishlist items
    wish_ids = wishlist_items.values_list('item_id', flat=True)

    # Fetch all Placed objects that match the list of IDs
    products = Placed.objects.filter(id__in=wish_ids)

    return render(request, "auctions/wishlist.html", {"products": products})