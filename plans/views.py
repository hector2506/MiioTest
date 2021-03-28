from plans.models import Plan
from plans.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class PlanList(APIView):
    """
    List all regular plans with publish = True or create a new regular plan.
    """

    def get(self, request, format=None):
        plans = Plan.objects.filter(publish=True)
        if(plans.count() > 0):
            serializer = PlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message":"The list of regular plans with publish = True is empty."},status=status.HTTP_200_OK)
        
    def post(self, request, format=None):
        serializer = PlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPlanList(APIView):
    """
    Lists a user's plans.
    """
    
    def get(self, request, pk, format=None):
            user = get_object_or_404(User, pk=pk)
            plans = Plan.objects.filter(owner=user)
            if plans:
                serializer = PlanSerializer(plans, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "This user doesn't have any plans."},status=status.HTTP_200_OK)


class PlanUpdate(APIView):
    """
    Update a regular plan.
    """

    def patch(self, request, pk, format=None):
        plan = get_object_or_404(Plan, pk=pk)
        if (plan.owner != None):
            serializer = PlanUpdateSerializer(plan, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_serializer = PlanSerializer(plan)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "This plan doesn't have an owner."},status=status.HTTP_405_METHOD_NOT_ALLOWED)