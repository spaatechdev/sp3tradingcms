from django.db import models


class Product_Type(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    header = models.TextField(blank=True, null=True)
    header_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_type_images/', blank=True, null=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product_type"  # Custom table name for ProductType


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    product_type = models.ForeignKey(Product_Type, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "product"  # Custom table name for Product
