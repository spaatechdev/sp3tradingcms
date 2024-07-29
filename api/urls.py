from rest_framework import routers
from django.urls import path
from django.conf.urls import include
from .views import ProductView, ProductTypeView
from rest_framework.authtoken import views

router = routers.DefaultRouter()
router.register('products', ProductView)
router.register('product-types', ProductTypeView)  # Register ProductTypeView

urlpatterns = [
    path('token-auth/', views.obtain_auth_token),
]

urlpatterns += router.urls
