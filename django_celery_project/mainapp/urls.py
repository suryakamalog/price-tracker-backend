
from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)   
app_name = "mainapp"

urlpatterns = [
    path('api/add_product/', views.product_add),
    path('api/user_product_list/', views.user_product_list),
    path('api/user_product/delete/', views.product_delete),
    path('api/register/', views.CustomUserCreate.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
