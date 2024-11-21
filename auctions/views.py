from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe

from .models import User, Listing, Category, Bid
from .forms import ListingForm

def index(request):
    cat = request.GET.get('cat')
    # when category is specified by GET Method
    if cat:
        listings = Listing.objects.filter(category=cat)
    else:
        listings = Listing.objects.all()

    # todo : must include current highest bid in each listings
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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

@login_required
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

@login_required
def create(request):
    """Create a Listing with an item."""
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # Set the user instance before saving
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html", {
        "form" : ListingForm()
    })


def listing(request):
    """Render detailed page for listing."""
    listing_id = request.GET.get('id')

    # only render active listings
    listing = Listing.objects.get(pk=listing_id)
    stat = listing.get_status_display()
    
    # todo : render status (active/closed)
    print(stat)

    """Give additional info about bids"""
    # show 3 highest bids
    if listing.bids.exists():
        current_bids = listing.bids.order_by('-price')[:5]
        bid_price = listing.bids.order_by('-price').first().price
        bid_user = listing.bids.order_by('-price').first().user
    else:
        current_bids = None
        bid_price = listing.start_price
        bid_user = None

    bid_enabled = True
    # give reasons for disabled bid buttons
    if not request.user.is_authenticated:
        login_url = reverse('login')
        messages.error(request, mark_safe(f"""You must be <a href="{login_url}">logged in</a> to bid."""))
        bid_enabled = False
    if listing.user == request.user:
        messages.error(request, "Sellers cannot bid on their own listings.")
        bid_enabled = False
    if bid_user == request.user:
        messages.error(request, "You are already the highest bidder.")
        bid_enabled = False
    

    return render(request, "auctions/listing.html", {
        "listing" : listing,
        "bids": listing.bids.all().count,
        "current_bids": current_bids,
        "bid_price": bid_price,
        "bid_user": bid_user,
        "bid_enabled": bid_enabled
    })

def category(request):
    categories = Category.objects.all()

    return render(request, "auctions/category.html", {
        "categories": categories
    })

@login_required
def bid(request):
    if request.method == 'POST':
        """
        Validate a bid from user
        If it is valid, add it to Bid DB.
        Send message to user if it succeeded
        """

        bid_amount = float(request.POST["bid_amount"])
        listing_id = request.POST['id']
        listing = Listing.objects.get(id=listing_id)
        oldbids = listing.bids.all()
        
        # validate bid
        if oldbids.exists():
            highest_bid = listing.bids.order_by('-price').first().price
            bidder = listing.bids.order_by('-price').first().user
            if bid_amount <= highest_bid:
                messages.error(request, "Your bid must be higher than the existing bid.")
                return HttpResponseRedirect(reverse("listing") + f"?id={listing_id}")
            elif request.user == bidder:
                messages.error(request, "You are already the highest bidder.")
                return HttpResponseRedirect(reverse("listing") + f"?id={listing_id}")
            else:
                newbid = Bid(user=request.user, listing=listing, price=bid_amount)
                newbid.save()
                
        else:
            if bid_amount >= listing.start_price:
                newbid = Bid(user=request.user, listing=listing, price=bid_amount)
                newbid.save()
            else:
                messages.error(request, "Your bid must be higher than or equal to the starting price.")
                
                return HttpResponseRedirect(reverse("listing") + f"?id={listing_id}")
        
        messages.success(request, "Your bid was accepted!")
        
    return HttpResponseRedirect(reverse("listing") + f"?id={listing_id}")