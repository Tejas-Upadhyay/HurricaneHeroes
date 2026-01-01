"""
Models for Hurricane Heroes Relief Management System
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


# Custom User model to support different user types
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('area_admin', 'Area Admin'),
        ('public', 'Public User'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Area Model
class Area(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=500)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    unit = models.CharField(max_length=50)  # kg, packets, boxes, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


# Area Admin Model
class AreaAdmin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='area_admin_profile')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='admins')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Area Admin'
        verbose_name_plural = 'Area Admins'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.area.name}"


# Need Model
class Need(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='needs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='needs')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='needs_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Need'
        verbose_name_plural = 'Needs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.area.name} ({self.quantity} {self.product.unit})"
    
    def get_category(self):
        """Helper method to get category from product"""
        return self.product.category


# Contact Model
class Contact(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('resolved', 'Resolved'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
