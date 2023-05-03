from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealers_by_id_from_cf, post_request
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password"
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['pwd']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/f02af28e-de7c-4b15-81b0-7a4731f2bf9c/dealership-package/get-dealerships.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        return render(request,'djangoapp/index.html', context)



# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/f02af28e-de7c-4b15-81b0-7a4731f2bf9c/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        dealer_url = "https://us-east.functions.appdomain.cloud/api/v1/web/f02af28e-de7c-4b15-81b0-7a4731f2bf9c/dealership-package/get-dealerships"
        dealers = get_dealers_by_id_from_cf(dealer_url, dealer_id)
        context ["dealers"] = dealers
        context ["reviews"] = reviews
        #return HttpResponse(context)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    dealer_url = "https://us-east.functions.appdomain.cloud/api/v1/web/f02af28e-de7c-4b15-81b0-7a4731f2bf9c/dealership-package/get-dealerships"
    post_url = "https://us-east.functions.appdomain.cloud/api/v1/web/f02af28e-de7c-4b15-81b0-7a4731f2bf9c/dealership-package/post-review"
    context = {}
    dealer = get_dealers_by_id_from_cf(dealer_url, dealer_id)
    context['dealer'] = dealer
    if request.method == 'GET':
        dealer = get_dealers_by_id_from_cf(dealer_url,dealer_id)
        cars = CarModel.objects.all()
        context["dealer"] = dealer
        context['cars'] = cars
        #return HttpResponse(context)
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            json_payload = {}
            review = {}
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = username
            review["dealership"] = dealer_id
            review["review"] = request.POST["content"]
            if "purchasecheck" in request.POST:
                review["purchase"] = True
            else:
                review["purchase"] = False
            review["purchase_date"] = request.POST.get('purchasedate','')
            review["car_make"] = car.make
            review["car_model"] = car.make.name
            review["car_year"] = int(car.year.strftime("%Y"))
            json_payload["review"] = review
            post_request(post_url, json_payload,dealer_id=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

