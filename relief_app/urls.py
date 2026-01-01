"""
URL configuration for relief_app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public/Front Panel
    path('', views.public_home, name='public_home'),
    path('about/', views.public_about, name='public_about'),
    path('services/', views.public_services, name='public_services'),
    path('contact/', views.public_contact, name='public_contact'),
    path('areas/', views.public_areas, name='public_areas'),
    path('area/<int:area_id>/', views.public_area_detail, name='public_area_detail'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Area Admin Panel
    path('area-admin/dashboard/', views.area_admin_dashboard, name='area_admin_dashboard'),
    path('area-admin/needs/', views.area_admin_needs, name='area_admin_needs'),
    path('area-admin/categories/', views.area_admin_categories, name='area_admin_categories'),
    path('area-admin/products/', views.area_admin_products, name='area_admin_products'),
    
    # Super Admin Panel
    path('super-admin/dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('super-admin/areas/', views.super_admin_areas, name='super_admin_areas'),
    path('super-admin/area-admins/', views.super_admin_area_admins, name='super_admin_area_admins'),
    path('super-admin/all-needs/', views.super_admin_all_needs, name='super_admin_all_needs'),
    path('super-admin/categories/', views.super_admin_categories, name='super_admin_categories'),
    path('super-admin/products/', views.super_admin_products, name='super_admin_products'),
    path('super-admin/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('super-admin/contacts/', views.super_admin_contacts, name='super_admin_contacts'),
    path('super-admin/need/<int:need_id>/view/', views.view_need_detail, name='view_need_detail'),
    path('super-admin/need/<int:need_id>/delete/', views.delete_need, name='delete_need'),
    path('super-admin/category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('super-admin/area/<int:area_id>/delete/', views.delete_area, name='delete_area'),
    path('super-admin/area-admin/<int:admin_id>/delete/', views.delete_area_admin, name='delete_area_admin'),
    path('super-admin/contact/<int:contact_id>/delete/', views.delete_contact, name='delete_contact'),
    path('super-admin/export-needs/<str:format>/', views.export_needs, name='export_needs'),
    path('super-admin/database/', views.database_management, name='database_management'),
    path('super-admin/database/export/', views.export_database, name='export_database'),
    path('super-admin/database/import/', views.import_database, name='import_database'),
]


