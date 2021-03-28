from celery import shared_task
from plans.mongo import *
from plans.models import Plan
from django.contrib.auth.models import User


@shared_task
def database_backup():
    db_handle, mongo_client = get_db_handle("Plans_DB")
    plans_handle = get_collection_handle(db_handle, "Plans")
    users_handle = get_collection_handle(db_handle, "Users")
    plans_handle.delete_many({})
    users_handle.delete_many({})
    if(Plan.objects.all().count() > 0):
        plans_data = list(Plan.objects.values())
        plans_handle.insert_many(plans_data)
    if(User.objects.all().count() > 0):
        users_data = list(User.objects.values())
        users_handle.insert_many(users_data)