from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
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
    user = get_object_or_404(User, username=request.user.username)
    winning_bids = user.winning_bids.all()
    winning_items = []
    for bid in winning_bids:
        try:
            # Retrieve the corresponding item in the Placed model
            item = Placed.objects.get(id=bid.item)
            winning_items.append(item)  # Add the item to the list
        except Placed.DoesNotExist:
            pass 
    
    

            
    # Create a dictionary to map item IDs to Placed objects for easy lookup

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
    return render(request, "auctions/index.html", {"listings": placed_listings,"winnings":winning_items})
    

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
            user = request.user

            # Attempt to convert price to float to ensure it is the correct type
            try:
                price = float(price)
            except ValueError:
                return render(request, "auctions/create_listing.html", {"not_filled": "Price must be a number"})

            # Create the listing instance
            listings_ = Placed(title=title, description=description, price=price, category=category, url=url, user=user)

            # Validate the image file extension
            if url and not str(url).lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                return render(request, "auctions/create_listing.html", {"not_filled": "Not a Valid Image File"})

            try:
                listings_.full_clean()  
                listings_.save()
                return HttpResponseRedirect(reverse('index'))
            except ValidationError as e:
                errors = e.message_dict
                error_message = "Fields Missing"
                if 'description' in errors and len(description) > 100:
                    error_message = "Keep Description Below 100 Characters"
                elif 'title' in errors and len(title) > 20:
                    error_message = "Keep Name Below 20 Characters"
                else:
                    error_message = errors
                return render(request, "auctions/create_listing.html", {"not_filled": error_message})

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
        return render(request, "auctions/listing.html", {"listings": info, "is_added": is_added,"user":user})
    else:
        return render(request, "auctions/listing.html", {"listings": info, "min_bid": min_bid,"is_added": is_added,"user":user})

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



def your_listings(request,username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        item = request.POST.get("remove")
        listing_ = Placed.objects.get(id=item)
        listing_.closed = True
        listing_.save()
    
        if listing_.current_bid is not None and listing_.closed:
            bid = Bids.objects.get(item=listing_.id,amount=listing_.current_bid)
            user = User.objects.get(username=bid.name)
            user.winning_bids.add(bid)


        return HttpResponseRedirect(reverse("your_listings", args=[username]))

    user = get_object_or_404(User, username=username)
    listings = Placed.objects.filter(user=user)

    return render(request, "auctions/your_listing.html", {"listings": listings})

def search(request):
    return render(request, "auctions/search.html", {})