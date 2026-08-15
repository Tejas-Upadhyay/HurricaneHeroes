"""
URL configuration for relief_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import FileResponse
from pathlib import Path

# Customize Admin Site
admin.site.site_header = "Hurricane Heroes - Admin Panel"
admin.site.site_title = "Hurricane Heroes Admin"
admin.site.index_title = "Relief Management System"

BASE_DIR = Path(__file__).resolve().parent.parent

def serve_sitemap(request):
    return FileResponse(open(BASE_DIR / 'sitemap.xml', 'rb'), content_type='application/xml')

def serve_robots(request):
    return FileResponse(open(BASE_DIR / 'robots.txt', 'rb'), content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', serve_sitemap),
    path('robots.txt', serve_robots),
    path('', include('relief_app.urls')),
]


