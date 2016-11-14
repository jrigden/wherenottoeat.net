import datetime


from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from .models import Inspection, Restaurant, Violation


def location(request, radius, lat, lng):
    template = loader.get_template('location.html')
    print("ssssssssssssssssssssssssssssssssssss")
    lat = float(lat)
    lng = float(lng)
    point = Point(lng, lat)
    restaurants = Restaurant.objects.exclude(Total_Violation_Points=0).exclude(Total_Violation_Points__isnull=True).filter(Location__distance_lt=(point, Distance(km=radius))).order_by('-Total_Violation_Points')
    print(len(restaurants))

    context = {
        'restaurants': restaurants,
        'radius': radius,
        'lat': lat,
        'lng': lng,
    }
    return HttpResponse(template.render(context, request))

def locate(request):
    template = loader.get_template('locate.html')
    context = {}
    return HttpResponse(template.render(context, request))

def index(request):
    template = loader.get_template('index.html')
    restaurants = Restaurant.objects.all()[:10:1]
    context = {
        'restaurants': restaurants,
    }
    return HttpResponse(template.render(context, request))

def inspection_detail(request, slug):
    inspection = get_object_or_404(Inspection, Inspection_Serial_Num=slug)
    violations = Violation.objects.filter(Inspection=inspection).order_by('-Inspection__Inspection_Date')
    template = loader.get_template('inspection_detail.html')
    context = {
        'inspection': inspection,
        'violations': violations
    }
    return HttpResponse(template.render(context, request))



def restaurant_detail(request, slug):
    restaurant = get_object_or_404(Restaurant, Business_ID=slug)
    inspections = Inspection.objects.filter(Restaurant=restaurant)
    violations = Violation.objects.filter(Inspection__Restaurant=restaurant).order_by('-Inspection__Inspection_Date')
    template = loader.get_template('restaurant_detail.html')
    context = {
        'inspections': inspections,
        'restaurant': restaurant,
        'violations': violations
    }
    return HttpResponse(template.render(context, request))
