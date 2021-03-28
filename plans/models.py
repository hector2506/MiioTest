from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from miiotest.mail_server import mail_send

class Plan(models.Model):
    cycle_options = [
        ("daily", "daily"),
        ("weekly", "weekly"),
    ]
    type_options = [
        ("bi-time", "bi-time"),
        ("tri-time", "tri-time"),
        ("simple", "simple"),
    ]
    unit_options = [
        ("kwh", "kwh"),
        ("min", "min"),
    ]
    name = models.CharField(max_length=50)
    tar_included = models.BooleanField()
    subscription = models.FloatField()
    cycle = models.CharField(max_length=25, choices=cycle_options)
    type_time = models.CharField(max_length=25, choices=type_options)
    offer_iva = models.BooleanField()
    off_peak_price = models.FloatField()
    peak_price = models.FloatField()
    unit = models.CharField(max_length=25, choices=unit_options)
    valid = models.BooleanField()
    publish = models.BooleanField()
    vat = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports", null=True, blank=True)

    def __str__(self):
        return "Plan " + str(self.id) + ": " + self.name


def save_plan(sender, instance, **kwargs):
    if (instance.publish == True) and (instance.owner != None):
        if instance.owner.email != "":
            mail_send(instance.name, instance.owner.email)
    if (instance.publish == False) and (instance.owner == None):
        raise Exception("No owner found.")


pre_save.connect(save_plan, sender=Plan)