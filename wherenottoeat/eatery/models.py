from django.contrib.gis.db import models


class Restaurant(models.Model):
    Address = models.CharField(max_length=75)
    Business_ID = models.CharField(max_length=50, unique=True)
    City = models.CharField(max_length=50)
    Description = models.CharField(max_length=75)
    Location = models.PointField(null=True, blank=True)
    Name = models.CharField(max_length=75)
    Program_Identifier = models.CharField(max_length=75)
    Zip_Code = models.CharField(max_length=50)

    Total_Inspection_Closed_Business = models.IntegerField(null=True, blank=True, default=None)
    Total_Violation_Points = models.IntegerField(null=True, blank=True, default=None)

class Inspection(models.Model):
    Inspection_Date = models.DateTimeField()
    Inspection_Closed_Business = models.BooleanField()
    Inspection_Result = models.CharField(max_length=50)
    Inspection_Score = models.IntegerField(null=True, blank=True, default=None)
    Inspection_Serial_Num = models.CharField(max_length=50, unique=True)
    Inspection_Type = models.CharField(max_length=50)
    Restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE)


class Violation(models.Model):
    Violation_Description = models.CharField(max_length=150)
    Violation_Points = models.IntegerField()
    Violation_Record_ID = models.CharField(max_length=50, unique=True)
    Violation_Type = models.CharField(max_length=50)

    Inspection = models.ForeignKey('Inspection', on_delete=models.CASCADE,)
