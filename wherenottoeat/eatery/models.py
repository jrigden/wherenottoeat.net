from django.contrib.gis.db import models


class Restaurant(models.Model):
    Address = models.CharField(max_length=50)
    Business_ID = models.CharField(max_length=50, unique=True)
    City = models.CharField(max_length=50)
    Description = models.CharField(max_length=50)
    Location = models.PointField(null=True, blank=True)
    Name = models.CharField(max_length=50)
    Program_Identifier = models.CharField(max_length=50, unique=True)
    Zip_Code = models.CharField(max_length=5)


class Inspection(models.Model):
    Inspection_Date = models.DateField()
    Inspection_Closed_Business = model.BooleanField()
    Inspection_Result = models.CharField(max_length=50)
    Inspection_Score = models.IntegerField()
    Inspection_Serial_Num = models.CharField(max_length=50, unique=True)
    Inspection Type = models.CharField(max_length=50)
    Restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE,)


class Violation(models.Model):
    Violation_Description = models.CharField(max_length=150)
    Violation_Points = models.IntegerField()
    Violation_Record_ID = models.CharField(max_length=50, unique=True)
    Violation_Type = models.CharField(max_length=50)

    Inspection = models.ForeignKey('Inspection', on_delete=models.CASCADE,)
