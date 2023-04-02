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

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'User {request.user} successfully registered')
            messages.success(request, "Registration successful." )
            return redirect("mainapp:homepage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
        logger.info(f'Unsuccessful registration. Invalid information.')
    form = NewUserForm()
    return render (request=request, template_name="mainapp/register.html", context={"register_form":form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("mainapp:homepage")
            else:
                messages.error(request,"Invalid username or password.")
                logger.info('Invalid username or password.')
        else:
            messages.error(request,"Invalid username or password.")
            logger.info('Invalid username or password.')
    form = AuthenticationForm()
    return render(request=request, template_name="mainapp/login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    logger.info(f'User {request.user} successfully logged out')
    messages.info(request, "You have successfully logged out.") 
    return redirect("mainapp:homepage")

def homepage(request):
    return render(request=request, template_name="mainapp/homepage.html")

def product_entry(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            request.user.product_set.add(product)
            price_scraping_task.delay(product.id)
            return redirect("mainapp:productlist")
        else:
            logger.info("Invalid Product form")
    return render(request, 'mainapp/addproduct.html', {'form':ProductForm})

def product_list(request):
    user = request.user
    product_list = user.product_set.all()
    return render(request, 'mainapp/productlist.html', {'products': product_list})



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
    print("insidde user_product_list api")
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
    pass




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
    
