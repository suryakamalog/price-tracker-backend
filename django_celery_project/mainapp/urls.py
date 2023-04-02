
from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)   
app_name = "mainapp"

urlpatterns = [
    path('productentry', views.product_entry, name='product-entry'),    
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    path('homepage', views.homepage, name='homepage'),
    path('productlist', views.product_list, name='productlist'),

    path('api-token-auth/', views.CustomAuthToken.as_view()),
    path('api/add_product/', views.product_add),
    path('api/user_product_list/', views.user_product_list),
    path('api/register/', views.CustomUserCreate.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
