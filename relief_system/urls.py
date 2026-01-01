"""
URL configuration for relief_system project.
"""
from django.contrib import admin
from django.urls import path, include

# Customize Admin Site
admin.site.site_header = "Hurricane Heroes - Admin Panel"
admin.site.site_title = "Hurricane Heroes Admin"
admin.site.index_title = "Relief Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('relief_app.urls')),
]


