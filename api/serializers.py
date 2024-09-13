from rest_framework import serializers
from .models import Product, Product_Type  # Import Product_Type model


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Type
        fields = ['id', 'name', 'description', 'header', 'header_description', 'image']


class ProductSerializer(serializers.ModelSerializer):
    product_type = ProductTypeSerializer(allow_null=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'product_type']
        extra_kwargs = {
            'image': {'required': False}
        }

