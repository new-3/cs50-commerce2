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
    status = request.GET.get('status')
    if status is None:
        status = Listing.ACTIVE

    listings = Listing.objects.filter(status=status)
    status_view = next(filter(lambda x: x[0] == status, Listing.STATUS))[1]
    
    cat = request.GET.get('cat')
    if cat:
        category_view = Category.objects.get(code=cat).name
    else:
        category_view = None

    # when category is specified by GET Method
    if cat:
        listings = listings.filter(category=cat)
    
    for listing in listings:
        if listing.bids.exists():
            listing.current_price = listing.bids.order_by('-price').first().price
        else:
            listing.current_price = None

    # todo : must include current highest bid in each listings
    return render(request, "auctions/index.html", {
        "listings": listings,
        "status_view": status_view,
        "category_view": category_view
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
    user, listing_id = request.user, request.GET.get('id')

    # only render active listings
    listing = Listing.objects.get(pk=listing_id)

    """Give additional info about bids"""
    # show 5 highest bids
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
    if not user.is_authenticated:
        login_url = reverse('login')
        messages.error(request, mark_safe(f"""You must be <a href="{login_url}">logged in</a> to bid."""))
        bid_enabled = False
    if listing.winner == request.user:
        messages.info(request, "You won the bid!")
        bid_enabled = False
    elif listing.status == Listing.CLOSED:
        messages.info(request, "Bid is Closed.")
        bid_enabled = False
    else:
        if listing.user == request.user:
            messages.error(request, "You cannot bid on your own listings.")
            bid_enabled = False
        if bid_user == request.user:
            messages.error(request, "You are already the highest bidder.")
            bid_enabled = False

    # toggle watchlists button
    is_watching = user.is_authenticated and user.watchlists.filter(id=listing.id).exists()
    
    return render(request, "auctions/listing.html", {
        "listing" : listing,
        "bids": listing.bids.all().count,
        "current_bids": current_bids,
        "bid_price": bid_price,
        "bid_user": bid_user,
        "bid_enabled": bid_enabled,
        "is_watching": is_watching
    })


@login_required
def close_bid(request):
    if request.method == 'POST':
        user, listing_id = request.user, request.POST.get('id')
        listing = Listing.objects.get(pk=listing_id)
        print(user, listing_id)
        if user != Listing.objects.get(pk=listing_id).user:
            messages.error(request, "Only the user who listed the item can close the bid!")
            return HttpResponseRedirect(reverse("listing") + f"?id={listing_id}")
        
        if listing.bids.exists():
            winner = listing.bids.order_by('-price').first().user
        else:
            winner = None

        listing.status = Listing.CLOSED
        listing.winner = winner
        listing.save()

        print(f"New Status: {listing.get_status_display()}, Winner: {listing.winner}")

        return HttpResponseRedirect(reverse("listing") + f"?id={listing_id}")

   
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

@login_required
def watchlist_view(request):

    return render(request, "auctions/watchlist.html", {
        "watchlists": request.user.watchlists.all(),
        "count": request.user.watchlists.count()
    })

@login_required
def watchlist_toggle(request):
    if request.method == "POST":
        user, id = request.user, request.POST["id"]
        listing = Listing.objects.get(pk=id)
        if user.watchlists.filter(id=listing.id).exists():
            user.watchlists.remove(listing)
        else:
            user.watchlists.add(listing)
        

    return HttpResponseRedirect(reverse("listing") + f"?id={listing.id}")