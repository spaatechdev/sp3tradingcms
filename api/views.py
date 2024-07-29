from .models import Product, Product_Type
from .serializers import ProductSerializer, ProductTypeSerializer
from rest_framework import viewsets, permissions
from rest_framework.response import Response
import os
from django.utils.text import slugify
from django.conf import settings
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class ProductTypeView(viewsets.ModelViewSet):
    queryset = Product_Type.objects.all()
    serializer_class = ProductTypeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


def delete_product_image(instance):
    # Delete the old image file
    if instance.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))
        if os.path.exists(image_path):
            os.remove(image_path)


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            product_type = Product_Type.objects.get(pk=data['product_type'])

            if Product.objects.filter(name=data['name']).exists():
                return Response({'error': 'Product with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            image = request.FILES.get('image')
            extension = image.name.split('.')[-1]
            image.name = f"{slugify(data['name'])}.{extension}"

            Product.objects.create(
                name=data['name'],
                description=data['description'],
                product_type=product_type,
                image=image
            )
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        paginate = request.query_params.get('paginate', 'false').lower() == 'true'

        if paginate:
            # Apply pagination
            paginator = PageNumberPagination()
            paginator.page_size = 10  # Number of items per page
            products = Product.objects.all()
            paginated_products = paginator.paginate_queryset(products, request)
            serializer = self.get_serializer(paginated_products, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            # Original functionality: return all products
            product_type_name = request.query_params.get('product_type', None)
            if product_type_name:
                products = Product.objects.filter(product_type__name__icontains=product_type_name)
            else:
                products = Product.objects.all()

            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_product_image(instance)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            product_type = Product_Type.objects.get(pk=data['product_type'])
            pk=self.kwargs['pk']
            product=Product.objects.get(pk=pk)
            if 'image' in request.FILES:
                delete_product_image(product)
                image = request.FILES.get('image')
                extension = image.name.split('.')[-1]
                image.name = f"{slugify(data['name'])}.{extension}"
                product.image = image
            else:
                if product.name != data['name']:
                    # Rename the existing image file
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
                    new_image_name = f"{slugify(data['name'])}.{product.image.name.split('.')[-1]}"
                    new_image_path = os.path.join(settings.MEDIA_ROOT, 'product_images', new_image_name)
                    if os.path.exists(old_image_path):
                        os.rename(old_image_path, new_image_path)
                    product.image.name = f'product_images/{new_image_name}'
            product.name=data['name']
            product.product_type=product_type
            product.description = data['description']
            product.save()
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

