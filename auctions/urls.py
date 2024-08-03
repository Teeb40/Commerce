from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing",views.create, name="create"),
    path("<str:title>/<int:id>", views.listing, name="listing"),
    path("watchlist/<str:username>", views.wishlist, name="wishlist")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
