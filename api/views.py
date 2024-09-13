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

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            # Check for unique name
            if Product_Type.objects.filter(name=data['name']).exists():
                return Response({'error_message': 'Product Type with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            image = request.FILES.get('image')
            if image:
                extension = image.name.split('.')[-1]
                image.name = f"{slugify(data['name'])}.{extension}"

            product_type = Product_Type.objects.create(
                name=data['name'],
                description=data['description'],
                header=data['header'],
                header_description=data['header_description'],
                image=image
            )
            return Response({'id': product_type.pk}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            # exit()
            instance = self.get_object()

            # Check for unique name
            if data['name'] != instance.name and Product_Type.objects.filter(name=data['name']).exists():
                return Response({'error_message': 'Product Type with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            if 'image' in request.FILES:
                # Delete old image if it exists
                if instance.image:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                image = request.FILES.get('image')
                extension = image.name.split('.')[-1]
                image.name = f"{slugify(data['name'])}.{extension}"
                instance.image = image

            instance.name = data['name']
            instance.description = data['description']
            instance.header = data['header']
            instance.header_description = data['header_description']
            instance.save()

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

            # Check for unique name
            if Product.objects.filter(name=data['name']).exists():
                return Response({'error_message': 'Product with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            image = request.FILES.get('image')
            if image:
                extension = image.name.split('.')[-1]
                image.name = f"{slugify(data['name'])}.{extension}"

            Product.objects.create(
                name=data['name'],
                description=data['description'],
                product_type=product_type,
                image=image
            )
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        paginate = request.query_params.get('paginate', 'false').lower() == 'true'

        # Apply pagination
        if paginate:
            products = Product.objects.all().order_by('id')
            product_type_id = request.query_params.get('product_type_id')
            keyword = request.query_params.get('keyword')

            if product_type_id:
                products = products.filter(product_type_id=product_type_id)
            if keyword:
                products = products.filter(name__icontains=keyword)

            paginator = PageNumberPagination()
            paginator.page_size = 10  # Number of items per page
            paginated_products = paginator.paginate_queryset(products, request)
            serializer = self.get_serializer(paginated_products, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Original functionality: return all products
        else:
            product_type_id = request.query_params.get('product_type_id', None)
            if product_type_id:
                products = Product.objects.filter(product_type_id=product_type_id)
            else:
                products = Product.objects.all()
                search_keyword = request.query_params.get('search_keyword', None)
                if search_keyword:
                    products = products.filter(name__istartswith=search_keyword)

            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = self.kwargs['pk']
            product = Product.objects.get(pk=pk)

            # Check for unique name
            if data['name'] != product.name and Product.objects.filter(name=data['name']).exists():
                return Response({'error_message': 'Product with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            if 'image' in request.FILES:
                # Delete old image if it exists
                if product.image:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                image = request.FILES.get('image')
                extension = image.name.split('.')[-1]
                image.name = f"{slugify(data['name'])}.{extension}"
                product.image = image

            product.name = data['name']
            product.product_type = Product_Type.objects.get(pk=data['product_type'])
            product.description = data['description']
            product.save()

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Delete the associated image file if it exists
        if instance.image:
            old_image_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        return super().destroy(request, *args, **kwargs)
