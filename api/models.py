from django.db import models
from django.utils.text import slugify
import os

class Product_Type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product_type"  # Custom table name for ProductType

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=10000)
    image = models.ImageField(upload_to='product_images/')  # Change here
    product_type = models.ForeignKey(Product_Type, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product"  # Custom table name for Product
