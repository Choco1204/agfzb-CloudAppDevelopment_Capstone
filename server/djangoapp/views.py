from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random
from .populate import initiate
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from .models import CarMake, CarModel
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


@login_required
def protected_view(request):
    return render(request, "djangoapp/protected.html")


def index(request):
    context = {}
    try:
        # Fetch dealership data from the API
        api_response = get_request("/fetchDealers")

        # Handle different response formats
        if api_response and isinstance(api_response, dict):
            dealers = api_response.get("dealers", [])
        elif api_response and isinstance(api_response, list):
            dealers = api_response
        else:
            dealers = []
            logger.warning("Unexpected API response format")

        # Extract unique states from the dealership data
        states = sorted(
            set(dealer.get("state") for dealer in dealers if dealer.get("state"))
        )

        # Filter dealerships by state if a state is provided in the query parameters
        selected_state = request.GET.get("state")
        if selected_state and selected_state != "All":
            dealers = [
                dealer for dealer in dealers if dealer.get("state") == selected_state
            ]

        # Add data to the context
        context["dealers"] = dealers
        context["states"] = states
        context["selected_state"] = selected_state or "All"  # Track the selected state

    except Exception as e:
        context["dealers"] = []
        context["states"] = []
        logger.error(f"Error fetching dealerships: {str(e)}")

    return render(request, "djangoapp/index.html", context)


#  get the list of cars
@csrf_exempt
def get_cars(request):
    try:
        # Check if we need to initialize sample data
        if CarMake.objects.count() == 0:
            initiate()  # Ensure this function exists and initializes data

        # Get car models with related makes
        car_models = CarModel.objects.select_related("make")
        cars = []

        for car_model in car_models:
            cars.append(
                {
                    "id": car_model.id,
                    "name": f"{car_model.make.name} {car_model.name} ({car_model.year})",  # Format: "Toyota Camry (2023)"
                }
            )

        return JsonResponse({"cars": cars})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/about.html", context)


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, "djangoapp/contact.html", {})


# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("djangoapp:protected")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "djangoapp/login.html", {"form": form})


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    print(get_template("djangoapp/base.html").origin)  # Debugging: Print template path
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("djangoapp:protected")
        else:
            messages.error(request, "Invalid information. Please try again.")
    else:
        form = CustomUserCreationForm()
    return render(request, "djangoapp/registration.html", {"form": form})


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request, state="All"):
    """
    Fetch dealerships from backend API
    """
    try:
        # Build endpoint based on state filter
        endpoint = f"/fetchDealers/{state}" if state != "All" else "/fetchDealers"

        # Get dealership data from external API
        dealerships = get_request(endpoint)

        if dealerships is None:
            return JsonResponse(
                {"status": 500, "error": "Failed to fetch dealerships"}, status=500
            )

        return JsonResponse({"status": 200, "dealers": dealerships})

    except Exception as e:
        return JsonResponse({"status": 500, "error": str(e)}, status=500)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    """
    Retrieve details for a specific dealership
    """
    try:
        # Construct endpoint URL
        endpoint = f"/fetchDealer/{dealer_id}"

        # Get dealer data from external API
        dealership = get_request(endpoint)

        if dealership is None:
            return JsonResponse(
                {"status": 404, "error": "Dealer not found"}, status=404
            )

        # Fetch reviews for the dealer
        reviews_endpoint = f"/fetchReviews/{dealer_id}"
        reviews = get_request(reviews_endpoint)

        # Render the dealer details template with dealer and reviews data
        return render(
            request,
            "djangoapp/dealer_details.html",
            {"dealer": dealership, "reviews": reviews if reviews else []},
        )

    except Exception as e:
        return JsonResponse({"status": 500, "error": str(e)}, status=500)


def get_dealer_reviews(request, dealer_id):
    """
    Retrieve reviews for a dealer with sentiment analysis
    """
    try:
        if not dealer_id:
            return JsonResponse(
                {"status": 400, "error": "Missing dealer_id parameter"}, status=400
            )

        # Get reviews from external API
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)

        if not reviews:
            return JsonResponse(
                {"status": 404, "error": "No reviews found"}, status=404
            )

        # Analyze sentiment for each review
        processed_reviews = []
        for review in reviews:
            if "review" in review:
                sentiment_response = analyze_review_sentiments(review["review"])
                review["sentiment"] = sentiment_response.get("sentiment", "neutral")
            else:
                review["sentiment"] = "neutral"  # Default if no review text
                logger.warning(f"Review {review.get('id')} missing review text")

            processed_reviews.append(review)

        return JsonResponse({"status": 200, "reviews": processed_reviews})

    except Exception as e:
        logger.error(f"Error processing reviews: {str(e)}")
        return JsonResponse(
            {"status": 500, "error": "Internal server error"}, status=500
        )


# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
    if request.method == "POST":
        try:
            # Generate a numeric ID (e.g., random number)
            review_id = random.randint(100000, 999999)  # Adjust range as needed

            # Extract form data
            review_data = {
                "id": review_id,  # Use a numeric ID
                "dealership": dealer_id,
                "name": request.POST.get("name"),
                "purchase": request.POST.get("purchase")
                == "on",  # Convert checkbox to boolean
                "review": request.POST.get("review"),
                "purchase_date": request.POST.get("purchase_date"),
                "car_model": request.POST.get("car_model"),
            }

            # Submit review
            result = post_review(review_data)
            if "error" in result:
                return JsonResponse(
                    {"status": 400, "error": result["error"]}, status=400
                )
            return JsonResponse(
                {"status": 201, "message": "Review added successfully"}, status=201
            )

        except Exception as e:
            return JsonResponse({"status": 500, "error": str(e)}, status=500)
    else:
        return JsonResponse(
            {"status": 405, "error": "Invalid request method"}, status=405
        )
