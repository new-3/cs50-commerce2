from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing
from .forms import ListingForm

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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
    """Create a Listing with an item."""
    if request.method == "POST":
        form = ListingForm(request.POST)
        print("hello")
        print("submitted")
        print(form)
        if form.is_valid():
            # Set the user instance before saving
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html", {
        "form" : ListingForm()
    })


def listing(request, listing_id):
    """Render detailed page for listing."""

    listing = Listing.objects.get(pk=listing_id)
    print(listing)
    stat = listing.get_status_display()
    print(stat)
    return render(request, "auctions/listing.html", {
        "listing" : listing
    })