from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = "djangoapp"

urlpatterns = [
    # =====================
    # Static Pages
    # =====================
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    # =====================
    # Authentication
    # =====================
    path("registration/", views.registration_request, name="registration"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    # =====================
    # Core Application
    # =====================
    path("", views.index, name="index"),
    path("protected/", views.protected_view, name="protected"),
    # =====================
    # Vehicle Endpoints
    # =====================
    path("cars/", views.get_cars, name="car_list"),
    # =====================
    # Dealership Endpoints
    # =====================
    path("dealers/", views.get_dealerships, name="dealers_list"),
    path("dealers/state/<str:state>/", views.get_dealerships, name="dealers_by_state"),
    path("dealers/<int:dealer_id>/", views.get_dealer_details, name="dealer_details"),
    # =====================
    # Review Endpoints
    # =====================
    path("reviews/<int:dealer_id>/", views.get_dealer_reviews, name="dealer_reviews"),
    path("add-review/<int:dealer_id>/", views.add_review, name="add_review"),
    # =====================
    # API endpoints (keep these separate)
    # =====================
    path("api/dealers/", views.get_dealerships, name="dealers_api"),
    path(
        "api/dealers/<str:state>/", views.get_dealerships, name="dealers_by_state_api"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
