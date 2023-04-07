from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProductForm, NewUserForm
from .tasks import price_scraping_task
from .models import Product
from .serializers import ProductSerializer
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .logger import logger
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import CustomUserSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from django.core.serializers import serialize
import json

class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def product_add(request):
    print(request.auth, request.user)
    if request.method == 'POST':
        serializer = ProductSerializer(data = request.data)
        if serializer.is_valid():
            
            print(f"User is {request.user}")
            if request.user.is_authenticated:
                print(f"User {request.user} is authenticated")
                product = serializer.save()
                request.user.product_set.add(product)
                price_scraping_task.delay(product.id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def user_product_list(request):
    print(request)
    if request.method == 'GET':
        if request.user.is_authenticated:
            print(f"User {request.user} is authenticated")
            product_list = request.user.product_set.all()
            product_serialize= json.loads(serialize('json', product_list))
            return Response({'data': product_serialize}, status=status.HTTP_201_CREATED)
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['PUT'])
def product_edit(request):
    pass
    
@api_view(['DELETE'])
def product_delete(request):
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            print(request.data)
            id = request.data['id']
            product = Product.objects.filter(id=id)
            if product:
                product.delete()
                return Response({'data': f'Product {id} deleted'}, status=status.HTTP_200_OK)
            else:
                return Response({'data': f'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


