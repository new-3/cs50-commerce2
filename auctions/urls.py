from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing", views.listing, name="listing"),
    path("category", views.category, name="category"),
    path("bid", views.bid, name="bid"),
    path("watch_toggle", views.watchlist_toggle, name="watch"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("close", views.close_bid, name="close"),
    path("comment", views.comment, name="comment"),
    path("del_comment", views.del_comment, name="del_comment")
]
