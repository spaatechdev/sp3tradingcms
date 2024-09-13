from django.contrib import admin

from .models import Product, Product_Type

admin.site.register(Product)
admin.site.register(Product_Type)