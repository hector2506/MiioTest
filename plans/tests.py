from django.test import TestCase
from django.contrib.auth.models import User
from plans.models import *
from plans.serializers import *
from plans.mongo import *
from unittest.mock import patch, Mock
from plans.tasks import database_backup


# Testing the Models
class ModelsTest(TestCase):

    def create_user_object(self, username="Test User", password="1234", email="test@test.com"):
        return User.objects.create(username=username, password=password, email=email)

    def create_plan_object(self, name="Teste", tar_included=True, subscription=55.5, cycle="daily", type_time="simple",
                           offer_iva=False, off_peak_price=35.3, peak_price=45.7, unit="min", valid=True,
                           publish=True, vat=25, owner=None):
        return Plan.objects.create(name=name, tar_included=tar_included, subscription=subscription, cycle=cycle, type_time=type_time,
                           offer_iva=offer_iva, off_peak_price=off_peak_price, peak_price=peak_price, unit=unit, valid=valid,
                           publish=publish, vat=vat, owner=owner)

    def test_user_creation(self):
        user = self.create_user_object()
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.__str__(), user.username)

    @patch("plans.models.mail_send")
    def test_plan_creation(self, mock_mail):
        user = self.create_user_object()
        plan = self.create_plan_object(owner=user)
        self.assertTrue(isinstance(plan, Plan))
        self.assertEqual(plan.__str__(), 
                        "Plan " + str(plan.id) + ": " + plan.name)
        mock_mail.assert_called_once()

    def test_plan_creation_invalid_no_owner(self):
        with self.assertRaises(Exception):
            user = self.create_user_object()
            plan = self.create_plan_object(publish=False, owner=None)


# Testing the Serializers
class SerializersTest(TestCase):
        
    def test_plan_serializer_valid(self):
        plan = PlanSerializer(data={"name":"Test", "tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,
                           "publish":True, "vat":25, "owner":None})
        self.assertTrue(plan.is_valid())

    def test_plan_serializer_invalid_missing_data(self):
        plan = PlanSerializer(data={"tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,
                           "publish":True, "vat":25, "owner":None})
        self.assertFalse(plan.is_valid())

    def test_plan_serializer_invalid_wrong_data(self):
        plan = PlanSerializer(data={"name": "Test", "tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,
                           "publish":1, "vat":-25, "owner":None})
        self.assertFalse(plan.is_valid())

    def test_plan_update_serializer_valid(self):
        plan = PlanSerializer(data={"name":"Test", "tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,
                           "publish":True, "vat":25})
        self.assertTrue(plan.is_valid())

    def test_plan_update_serializer_invalid_missing_data(self):
        plan = PlanSerializer(data={"tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,})
        self.assertFalse(plan.is_valid())

    def test_plan_update_serializer_invalid_wrong_data(self):
        plan = PlanSerializer(data={"name": "Test", "tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,
                           "publish":1, "vat":-25})
        self.assertFalse(plan.is_valid())


# Testing the API
class APITest(TestCase):
    
    def create_plan_object(self, name="Teste", tar_included=True, subscription=55.5, cycle="daily", type_time="simple",
                           offer_iva=False, off_peak_price=35.3, peak_price=45.7, unit="min", valid=True,
                           publish=True, vat=25, owner=None):
        return Plan.objects.create(name=name, tar_included=tar_included, subscription=subscription, cycle=cycle, type_time=type_time,
                           offer_iva=offer_iva, off_peak_price=off_peak_price, peak_price=peak_price, unit=unit, valid=valid,
                           publish=publish, vat=vat, owner=owner)
        
    def create_user_object(self, username="Test User", password="1234", email="test@test.com"):
        return User.objects.create(username=username, password=password, email=email)
    
    def create_plan_serializer(self):
        return PlanSerializer(data={"name":"Teste", "tar_included":True, "subscription":55.5, "cycle":"daily", "type_time":"simple",
                           "offer_iva":False, "off_peak_price":35.3, "peak_price":45.7, "unit":"min", "valid":True,
                           "publish":True, "vat":25, "owner":None})
        
    def test_plan_list_get_okay(self):
        self.create_plan_object()
        response = self.client.get('/plans/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONNotEqual(response.content, {"message":"The list of regular plans with publish = True is empty."})
        
    def test_plan_list_get_no_plans(self):
        response = self.client.get('/plans/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message":"The list of regular plans with publish = True is empty."})
        
    def test_plan_list_post_okay(self):
        serializer = self.create_plan_serializer()
        response = self.client.post('/plans/', data=serializer.initial_data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_plan_list_post_invalid_wrong_data(self):
        response = self.client.post('/plans/', data={"name":"Teste", "tar_included":True, "subscription":55.5, "cycle":"daily",
                                                "type_time":"simple","offer_iva":False, "off_peak_price":35.3, "peak_price":45.7,
                                                "unit":"min", "valid":True, "publish":True, "vat":-25, "owner":None},
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
    
    def test_plan_list_post_invalid_missing_data(self):
        response = self.client.post('/plans/', data={"tar_included":True, "subscription":55.5, "cycle":"daily",
                                                "type_time":"simple","offer_iva":False, "off_peak_price":35.3, "peak_price":45.7,
                                                "valid":True, "publish":True, "vat":-25, "owner":None},
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_user_plan_list_get_okay(self):
        user = self.create_user_object()
        self.create_plan_object(owner=user)
        self.create_plan_object(name="Teste 2", publish=False, owner=user)
        response = self.client.get('/plans/users/'+str(user.id)+"/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONNotEqual(response.content, {"message":"This user doesn't have any plans."})
    
    def test_user_plan_list_get_no_plans(self):
        user = self.create_user_object()
        response = self.client.get('/plans/users/'+str(user.id)+"/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message":"This user doesn't have any plans."})
    
    def test_user_plan_list_get_no_user(self):
        response = self.client.get('/plans/users/1/')
        self.assertEqual(response.status_code, 404)
        
    def test_plan_update_okay(self):
        user = self.create_user_object()
        plan = self.create_plan_object(owner=user)
        response = self.client.patch('/plans/'+str(plan.id)+'/', data={"name":"Updated Test"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"id": plan.id, "name":"Updated Test", "tar_included":True, "subscription":55.5, "cycle":"daily",
                                                "type_time":"simple","offer_iva":False, "off_peak_price":35.3, "peak_price":45.7,
                                                "unit":"min", "valid":True, "publish":True, "vat":25, "owner":user.id})
        
    def test_plan_update_invalid(self):
        user = self.create_user_object()
        plan = self.create_plan_object(owner=user)
        response = self.client.patch('/plans/'+str(plan.id)+'/', data={"vat":-5}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_plan_update_no_user(self):
        plan = self.create_plan_object()
        response = self.client.patch('/plans/'+str(plan.id)+'/', data={"name":"Updated Test"}, content_type="application/json")
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "This plan doesn't have an owner."})
        

# Testing the Tasks
class TasksTest(TestCase):
    def create_user_object(self, username="Test User", password="1234", email="test@test.com"):
        return User.objects.create(username=username, password=password, email=email)

    def create_plan_object(self, name="Teste", tar_included=True, subscription=55.5, cycle="daily", type_time="simple",
                           offer_iva=False, off_peak_price=35.3, peak_price=45.7, unit="min", valid=True,
                           publish=True, vat=25, owner=None):
        return Plan.objects.create(name=name, tar_included=tar_included, subscription=subscription, cycle=cycle, type_time=type_time,
                           offer_iva=offer_iva, off_peak_price=off_peak_price, peak_price=peak_price, unit=unit, valid=valid,
                           publish=publish, vat=vat, owner=owner)

    @patch("plans.tasks.get_collection_handle")
    def test_mongo_no_data(self, mock_handle):
        delete_mock = Mock(name='delete')
        connection_handle = Mock(name='collection', delete_many=delete_mock)
        mock_handle.return_value = connection_handle
        database_backup()
        self.assertEqual(mock_handle.call_count, 2)
        self.assertEqual(delete_mock.call_count, 2)
        
    @patch("plans.tasks.get_collection_handle")
    def test_mongo_user(self, mock_handle):
        self.create_user_object()
        insert_mock = Mock(name='insert')
        delete_mock = Mock(name='delete')
        connection_handle = Mock(name='collection', delete_many=delete_mock, insert_many=insert_mock)
        mock_handle.return_value = connection_handle
        database_backup()
        self.assertEqual(mock_handle.call_count, 2)
        self.assertEqual(delete_mock.call_count, 2)
        self.assertEqual(insert_mock.call_count, 1)
    
    @patch("plans.tasks.get_collection_handle")
    def test_mongo_plan(self, mock_handle):
        self.create_plan_object()
        insert_mock = Mock(name='insert')
        delete_mock = Mock(name='delete')
        connection_handle = Mock(name='collection', delete_many=delete_mock, insert_many=insert_mock)
        mock_handle.return_value = connection_handle
        database_backup()
        self.assertEqual(mock_handle.call_count, 2)
        self.assertEqual(delete_mock.call_count, 2)
        self.assertEqual(insert_mock.call_count, 1)
        
    @patch("plans.tasks.get_collection_handle")
    def test_mongo_plan_user(self, mock_handle):
        self.create_user_object()
        self.create_plan_object()
        insert_mock = Mock(name='insert')
        delete_mock = Mock(name='delete')
        connection_handle = Mock(name='collection', delete_many=delete_mock, insert_many=insert_mock)
        mock_handle.return_value = connection_handle
        database_backup()
        self.assertEqual(mock_handle.call_count, 2)
        self.assertEqual(delete_mock.call_count, 2)
        self.assertEqual(insert_mock.call_count, 2)