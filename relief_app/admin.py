"""
Django Admin configuration for Hurricane Heroes Relief Management System
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Area, Product, Need, AreaAdmin, Contact


# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active', 'date_joined')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('user_type',)}),
    )


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


# Area Admin
@admin.register(Area)
class AreaModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'address', 'pincode', 'created_at')
    search_fields = ('name', 'address', 'pincode')
    list_filter = ('created_at',)


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'description', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('category', 'created_at')
    autocomplete_fields = ['category']


# Area Admin Profile Admin
@admin.register(AreaAdmin)
class AreaAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'area', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'area__name')
    list_filter = ('is_active', 'area', 'created_at')
    autocomplete_fields = ['user', 'area']


# Need Admin
@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = ('product', 'area', 'quantity', 'priority', 'status', 'created_by', 'created_at')
    search_fields = ('product__name', 'area__name', 'notes')
    list_filter = ('priority', 'status', 'created_at', 'area')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['area', 'product', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('area', 'product', 'quantity')
        }),
        ('Details', {
            'fields': ('priority', 'status', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        """Allow area admins to change their own area's needs"""
        if request.user.user_type == 'super_admin':
            return True
        if request.user.user_type == 'area_admin' and obj:
            try:
                area_admin = AreaAdmin.objects.get(user=request.user)
                return obj.area == area_admin.area
            except AreaAdmin.DoesNotExist:
                return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow area admins to delete their own area's needs"""
        if request.user.user_type == 'super_admin':
            return True
        if request.user.user_type == 'area_admin' and obj:
            try:
                area_admin = AreaAdmin.objects.get(user=request.user)
                return obj.area == area_admin.area
            except AreaAdmin.DoesNotExist:
                return False
        return True


# Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

