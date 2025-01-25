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

from .populate import initiate
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from .models import CarMake, CarModel
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


@login_required
def protected_view(request):
    return render(request, "djangoapp/protected.html")


#  get the list of cars
@csrf_exempt
def get_cars(request):
    try:
        # Check if we need to initialize sample data
        if CarMake.objects.count() == 0:
            initiate()
            # Create sample data directly instead of calling undefined initiate()
            toyota = CarMake.objects.create(
                name="Toyota",
                description="Japanese automotive manufacturer",
                country_of_origin="Japan",
            )

            CarModel.objects.create(
                make=toyota, dealer_id=1, name="Camry", type="Sedan", year=2023
            )

        # Get car models with related makes using correct field name 'make'
        car_models = CarModel.objects.select_related("make")
        cars = []

        for car_model in car_models:
            cars.append(
                {
                    "CarModel": car_model.name,
                    "CarMake": car_model.make.name,  # Correct field name 'make' instead of 'car_make'
                }
            )

        return JsonResponse({"CarModels": cars})

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
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
