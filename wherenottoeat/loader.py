# Logging Boilerplate
import logging
import coloredlogs
LOG_FORMAT = '%(asctime)s  %(levelname)-8s  %(message)s'
LOG_DATE = "%Y-%m-%d %H:%M:%S"
LOG_STYLE = dict(
    debug=dict(color='cyan', bold=True),
    info=dict(color='green', bold=True),
    verbose=dict(color='white'),
    warning=dict(color='yellow', bold=True),
    error=dict(color='red', bold=True),
    critical=dict(color='magenta', bold=True))

logger = logging.getLogger('logging_template')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT, LOG_DATE)

fileHander = logging.FileHandler('podir_loader.log')
fileHander.setLevel(logging.INFO)
fileHander.setFormatter(formatter)
logger.addHandler(fileHander)

coloredlogs.install(level='DEBUG', fmt=LOG_FORMAT,
                    datefmt=LOG_DATE, level_styles=LOG_STYLE)

# General Imports
import csv
from datetime import datetime
import os
from time import mktime


import parsedatetime
import django
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from geopy.geocoders import Nominatim, GoogleV3
import psycopg2
import pytz
from pytz import timezone

cal = parsedatetime.Calendar()
geolocator = GoogleV3(api_key='')
geolocator_beta = Nominatim()


os.environ['DJANGO_SETTINGS_MODULE'] = 'wherenottoeat.settings'
django.setup()

from eatery.models import Restaurant, Inspection, Violation
import eatery.models

def load_data():
    with open('FOOD.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            add_violation(row)

def get_or_add_restaurant(row):
    logger.info("Attempting to add restaurant with Business_ID: " + row['Business_ID'])

    restaurant = Restaurant()

    try:
        Longitude = float(row['Longitude'])
        Latitude = float(row['Latitude'])
    except ValueError:
        long_address = row['Address'] + ", " + row['City'] + ", " + "Wa"
        #print(long_address)
        location = geolocator.geocode(long_address)
        #print(location)
        if location is None:
            location = geolocator_beta.geocode(long_address)
        if location is None:
            logger.critical("Critical: could not geocode Business_ID: " + row['Business_ID'])
            Longitude = 0
            Latitude = 0
        else:
            Longitude = location.longitude
            Latitude = location.longitude
    point = Point(Longitude, Latitude)

    restaurant.Address = row['Address']
    restaurant.Business_ID = row['Business_ID']
    restaurant.City = row['City']
    restaurant.Description = row['Description']
    restaurant.Location = point
    restaurant.Name = row['Name']
    restaurant.Program_Identifier = row['Program Identifier']
    restaurant.Zip_Code = row['Zip Code']
    try:
        restaurant.save()
        logger.info("Saved new restaurant with ID: " + str(restaurant.id))
        return restaurant
    except django.db.utils.IntegrityError:
        logger.error("Duplicate restaurant with Business_ID: " + row['Business_ID'])
        restaurant = Restaurant.objects.get(Business_ID=row['Business_ID'])
        return restaurant


def get_or_add_inspection(row):
    logger.info("Attempting to add inspection with Inspection_Serial_Num: " + row['Inspection_Serial_Num'])
    restaurant = get_or_add_restaurant(row)

    inspection = Inspection()

    inspection_date, parse_status = cal.parseDT(datetimeString=row['Inspection Date'], tzinfo=timezone("US/Pacific"))
    inspection.Inspection_Date = inspection_date

    if row['Inspection Closed Business'].lower() == "True":
        inspection.Inspection_Closed_Business = True
    else:
        inspection.Inspection_Closed_Business = False

    inspection.Inspection_Result = row['Inspection Result']
    if row['Inspection Score']:
        inspection.Inspection_Score = row['Inspection Score']
    else:
        inspection.Inspection_Score = None
    inspection.Inspection_Serial_Num = row['Inspection_Serial_Num']
    inspection.Inspection_Type = row['Inspection Type']
    inspection.Restaurant = restaurant
    try:
        inspection.save()
        logger.info("Saved new inspection with ID: " + str(inspection.id))
        return inspection
    except django.db.utils.IntegrityError:
        logger.error("Duplicate inspection with Inspection_Serial_Num: " + row['Inspection_Serial_Num'])
        inspection = Inspection.objects.get(Inspection_Serial_Num=row['Inspection_Serial_Num'])
        return inspection


def add_violation(row):
    inspection = get_or_add_inspection(row)
    if not row['Violation_Record_ID']:
        logger.info("This entry is not a violation")
        return
    logger.info("Attempting to add violation with Violation_Record_ID: " + row['Violation_Record_ID'])

    violation = Violation()
    violation.Violation_Description = row['Violation Description']
    violation.Violation_Points = row['Violation Points']
    violation.Violation_Record_ID = row['Violation_Record_ID']
    violation.Violation_Type = row['Violation Type']
    violation.Inspection = inspection
    try:
        violation.save()
        logger.info("Saved new violation with ID: " + str(violation.id))
        return violation
    except django.db.utils.IntegrityError:
        logger.error("Duplicate violation with Violation_Record_ID: " + row['Violation_Record_ID'])
        violation = Violation.objects.get(Violation_Record_ID=row['Violation_Record_ID'])
        return violation






def get_counts():
    restaurant_count = Restaurant.objects.count()
    print(restaurant_count)
    inspection_count = Inspection.objects.count()
    print(inspection_count)
    violation_count = Violation.objects.count()
    print(violation_count)

def random_rest():
    restaurant = Restaurant.objects.order_by('?').first()

    set_Total_Violation_Points(restaurant)
    set_Total_Inspection_Closed_Business(restaurant)

def update_all_restaurant_total_scores():
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        restaurant.Total_Violation_Points = set_Total_Violation_Points(restaurant)
        restaurant.Total_Inspection_Closed_Business = set_Total_Inspection_Closed_Business(restaurant)
        restaurant.save()
        print("############################")
        print("############################")
        print(restaurant.id)
        print(restaurant.Total_Violation_Points)
        check_restaurant = Restaurant.objects.get(id=restaurant.id)
        print(check_restaurant.Total_Violation_Points)


def set_Total_Violation_Points(restaurant):
    logger.info("Calculating Total_Violation_Points for: " + restaurant.Name)
    total = 0
    violation_query = Violation.objects.filter(Inspection__Restaurant=restaurant)
    for violation in violation_query:
        total = total + violation.Violation_Points
    logger.info("Total_Violation_Points: " + str(total))
    return total

def set_Total_Inspection_Closed_Business(restaurant):
    logger.info("Calculating Inspection_Closed_Business for: " + restaurant.Name)
    count = Inspection.objects.filter(Restaurant=restaurant, Inspection_Closed_Business=True).count()
    logger.info("Total_Inspection_Closed_Business: " + str(count))
    return count

question = Restaurant.objects.filter(Name__icontains='ASIA GINGER')
for each in question:
    print(each.Name)

#
# restaurant = Restaurant.objects.order_by('?').first()
# print(restaurant.Location)
#
#
# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
#
# lng = -122.1305
# lat = 47.6187
# point = Point(lng, lat)
# radius = 1
# #query = Restaurant.objects.exclude(Total_Violation_Points__isnull=True).filter(Location__distance_lt=(point, Distance(km=radius))).order_by('-Total_Violation_Points')
# query = Restaurant.objects.exclude(Total_Violation_Points=0).exclude(Total_Violation_Points__isnull=True).filter(Location__distance_lt=(point, Distance(km=radius))).order_by('-Total_Violation_Points')
#
# for each in query:
#     print('K')
#     print(each.Name)
#     print(each.Total_Violation_Points)
# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
# exit()
# query = Restaurant.objects.exclude(Total_Violation_Points__isnull=True).order_by('-Total_Violation_Points').first()
# print(query.Name)
# print(query.Total_Violation_Points)
# exit()
# for each in query:
#     print(each.Total_Violation_Points)
#
#
# #check_restaurant = Restaurant.objects.get(id=18056)
# #print(check_restaurant.Total_Violation_Points)
# # update_all_restaurant_total_scores()
# # restaurants = Restaurant.objects.all()
# # for restaurant in restaurants:
# #     print(restaurant.Total_Violation_Points)
