from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass


class Category(models.Model):
    """Restricts length of code field to exactly 3. """
    def validate_code_len(value):
        if len(value) != 3:
            raise ValidationError(f"Code must be exactly 3 characters long.")
    
    code = models.CharField(max_length=3, validators=[validate_code_len])
    name = models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.name

def get_category_choices():
    return [(category.code, category.name) for category in Category.objects.all()]


class Listing(models.Model):
    ACTIVE = "A"
    CLOSED = "C"
    STATUS = [
        (ACTIVE, "Active"),
        (CLOSED, "Closed")
    ]
    
    title = models.CharField(max_length=30, help_text="Enter a name of item.")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    desc = models.TextField(help_text="Please describe information about your item.")
    status = models.CharField(max_length=1, choices=STATUS, default=ACTIVE)
    start_price = models.DecimalField(max_digits=7, decimal_places=2, help_text="Enter the starting bid should be.")
    image_url = models.URLField(blank=True, help_text="Please provide the URL of your item(optional).")
    category = models.CharField(max_length=3, blank=True, choices=get_category_choices(), help_text="Select the category of your item(optional).")
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(max_digits=7, decimal_places=2, help_text="How much do you bid?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"${self.price} for ${self.listing} by {self.user}" 


class Comment(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, models.CASCADE, related_name="comments")
    content = models.TextField(help_text="Leave your comment with kind words :)")
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.content[:10]


class WatchList(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="watching_item")
    listing = models.ForeignKey(Listing, models.CASCADE, related_name="watched_by")

    def __str__(self) -> str:
        return f"{self.user} - {self.listing}"


# Complete the implementation of your auction site. You must fulfill the following requirements:

# Models: Your application should have at least three models in addition to the User model: one for auction listings, one for bids, 
# and one for comments made on auction listings. It’s up to you to decide what fields each model should have, 
# and what the types of those fields should be. You may have additional models if you would like.

# Create Listing: Users should be able to visit a page to create a new listing. They should be able to specify a title for the listing, 
# a text-based description, and what the starting bid should be. Users should also optionally be able to provide a URL for an image for 
# the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.).
# Active Listings Page: The default route of your web application should let users view all of the currently active auction listings. 
# For each active listing, this page should display (at minimum) the title, description, current price, and photo (if one exists for the listing).

# Listing Page: Clicking on a listing should take users to a page specific to that listing. 
# On that page, users should be able to view all details about the listing, including the current price for the listing.

# If the user is signed in, the user should be able to add the item to their “Watchlist.” 
# If the item is already on the watchlist, the user should be able to remove it.
# If the user is signed in, the user should be able to bid on the item. The bid must be at least as large as the starting bid, 
# and must be greater than any other bids that have been placed (if any). If the bid doesn’t meet those criteria, the user should be presented with an error.

# If the user is signed in and is the one who created the listing, 
# the user should have the ability to “close” the auction from this page, 
# which makes the highest bidder the winner of the auction and makes the listing no longer active.

# If a user is signed in on a closed listing page, and the user has won that auction, the page should say so.

# Users who are signed in should be able to add comments to the listing page. 
# The listing page should display all comments that have been made on the listing.

# Watchlist: Users who are signed in should be able to visit a Watchlist page, 
# which should display all of the listings that a user has added to their watchlist. 
# Clicking on any of those listings should take the user to that listing’s page.

# Categories: Users should be able to visit a page that displays a list of all listing categories. 
# Clicking on the name of any category should take the user to a page that displays all of the active listings in that category.

# Django Admin Interface: Via the Django admin interface, a site administrator should be able to view, add, edit, 
# and delete any listings, comments, and bids made on the site.