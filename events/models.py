from django.db import models

# Create your models here.

class Vendor(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField("Event date")
    start = models.TimeField("Event start time")
    end = models.TimeField("Event end time")
    location = models.CharField(max_length=200)

    class Meta:
        unique_together = ("name", "date")

    def __str__(self):
        return str(self.name + " --- " + self.date.isoformat() + 
                    " --- " + self.location)

class Event_Vendor(models.Model):
    event = models.ForeignKey(Event)
    vendor = models.ForeignKey(Vendor)

    class Meta:
        unique_together = ("event", "vendor")

    def __str__(self):
        return str(self.event) + " --- " + str(self.vendor)

