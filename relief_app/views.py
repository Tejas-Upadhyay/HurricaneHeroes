"""
Views for Hurricane Heroes
All data is now dynamic from database
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Case, When, IntegerField
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from pathlib import Path
import csv
import json
import sqlite3
import os
from datetime import datetime

# Get BASE_DIR (parent of relief_app, which is parent of relief_system)
BASE_DIR = Path(__file__).resolve().parent.parent

from .models import Area, Category, Product, Need, AreaAdmin, Contact
from django.contrib.auth import get_user_model

User = get_user_model()


def get_statistics():
    """Calculate statistics for dashboard"""
    total_areas = Area.objects.count()
    total_needs = Need.objects.count()
    total_products = Product.objects.count()
    total_area_admins = AreaAdmin.objects.filter(is_active=True).count()
    
    return {
        'total_areas': total_areas,
        'total_needs': total_needs,
        'total_products': total_products,
        'total_area_admins': total_area_admins,
    }


# Public Views
def public_home(request):
    """Home page for public users with filtering and sorting"""
    stats = get_statistics()
    
    # Get filter parameters
    region_filter = request.GET.get('region', '')
    category_filter = request.GET.get('category', '')
    priority_filter = request.GET.get('priority', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Start with all needs
    needs_query = Need.objects.select_related('product', 'area', 'product__category').filter(status__in=['pending', 'in_progress'])
    
    # Apply filters
    if region_filter:
        needs_query = needs_query.filter(area_id=region_filter)
    if category_filter:
        needs_query = needs_query.filter(product__category_id=category_filter)
    if priority_filter:
        needs_query = needs_query.filter(priority=priority_filter)
    
    # Apply sorting
    if sort_by == 'priority':
        # Custom ordering: urgent > high > medium > low
        needs_query = needs_query.annotate(
            priority_order=Case(
                When(priority='urgent', then=4),
                When(priority='high', then=3),
                When(priority='medium', then=2),
                When(priority='low', then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by('-priority_order', '-created_at')
    elif sort_by == 'area':
        needs_query = needs_query.order_by('area__name', '-created_at')
    elif sort_by == 'category':
        needs_query = needs_query.order_by('product__category__name', '-created_at')
    else:
        needs_query = needs_query.order_by('-created_at')
    
    # Get all filtered needs (for display)
    all_needs = needs_query[:50]  # Limit to 50 for performance
    
    # Enrich needs with product and category info
    enriched_needs = []
    for need in all_needs:
        enriched_needs.append({
            'need': need,
            'product': need.product,
            'category': need.product.category if need.product else None,
            'area': need.area,
        })
    
    # Get filter options
    all_areas = Area.objects.all().order_by('name')
    all_categories = Category.objects.all().order_by('name')
    
    context = {
        'stats': stats,
        'recent_needs': enriched_needs,
        'all_areas': all_areas,
        'all_categories': all_categories,
        'selected_region': region_filter,
        'selected_category': category_filter,
        'selected_priority': priority_filter,
        'sort_by': sort_by,
    }
    return render(request, 'public/home.html', context)


def public_areas(request):
    """List all areas for public view"""
    areas = Area.objects.annotate(needs_count=Count('needs')).order_by('name')
    context = {
        'areas': areas,
    }
    return render(request, 'public/areas.html', context)


def public_area_detail(request, area_id):
    """Show area detail with needs"""
    area = get_object_or_404(Area, id=area_id)
    
    # Get needs for this area with related data
    area_needs = Need.objects.filter(area=area).select_related('product', 'product__category')
    
    context = {
        'area': area,
        'needs': area_needs,
        'total_needs': area_needs.count(),
    }
    return render(request, 'public/area_detail.html', context)


def public_about(request):
    """About page for public users"""
    stats = get_statistics()
    context = {
        'stats': stats,
    }
    return render(request, 'public/about.html', context)


def public_services(request):
    """Services page for public users"""
    categories = Category.objects.all()
    stats = get_statistics()
    context = {
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'public/services.html', context)


def public_contact(request):
    """Contact page for public users"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            try:
                # Save contact form submission to database
                contact = Contact.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                    status='new'
                )
                messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            except Exception as e:
                messages.error(request, f'Error saving your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    areas = Area.objects.all()
    context = {
        'areas': areas,
    }
    return render(request, 'public/contact.html', context)


# Authentication Views
def login_view(request):
    """Login view with proper authentication"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['user_type'] = user.user_type
                
                if user.user_type == 'super_admin':
                    return redirect('super_admin_dashboard')
                elif user.user_type == 'area_admin':
                    return redirect('area_admin_dashboard')
                else:
                    return redirect('public_home')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please provide username and password')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('public_home')


# Area Admin Views
@login_required
def area_admin_dashboard(request):
    """Dashboard for Shelter Admin"""
    if request.user.user_type != 'area_admin':
        messages.error(request, 'Access denied. Please login as Shelter Admin.')
        return redirect('login')
    
    # Get area admin profile
    try:
        area_admin_profile = AreaAdmin.objects.get(user=request.user)
        area = area_admin_profile.area
    except AreaAdmin.DoesNotExist:
        messages.error(request, 'Area admin profile not found')
        return redirect('login')
    
    # Get needs for this area
    area_needs = Need.objects.filter(area=area).select_related('product', 'product__category')
    
    context = {
        'area': area,
        'needs': area_needs,
        'total_needs': area_needs.count(),
        'categories': Category.objects.all(),
        'products': Product.objects.select_related('category'),
        'area_admin_profile': area_admin_profile,
    }
    return render(request, 'area_admin/dashboard.html', context)


@login_required
def area_admin_needs(request):
    """Manage needs for area admin"""
    if request.user.user_type != 'area_admin':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get area admin profile
    try:
        area_admin_profile = AreaAdmin.objects.get(user=request.user)
        area = area_admin_profile.area
    except AreaAdmin.DoesNotExist:
        messages.error(request, 'Area admin profile not found')
        return redirect('login')
    
    # Handle POST request to create/update need
    if request.method == 'POST':
        need_id = request.POST.get('need_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        priority = request.POST.get('priority', 'medium')
        notes = request.POST.get('notes', '')
        
        try:
            product = Product.objects.get(id=product_id)
            
            if need_id:  # Update existing need
                need = Need.objects.get(id=need_id, area=area)
                need.product = product
                need.quantity = int(quantity)
                need.priority = priority
                need.notes = notes
                need.save()
                messages.success(request, f'Need updated successfully!')
            else:  # Create new need
                need = Need.objects.create(
                    area=area,
                    product=product,
                    quantity=int(quantity),
                    priority=priority,
                    notes=notes,
                    created_by=request.user,
                    status='pending'
                )
                messages.success(request, f'New need for {product.name} added successfully!')
            
        except Product.DoesNotExist:
            messages.error(request, 'Selected product not found')
        except Need.DoesNotExist:
            messages.error(request, 'Need not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        # Redirect to prevent duplicate submissions
        return redirect('area_admin_needs')
    
    # Get needs for this area with enriched data
    area_needs = Need.objects.filter(area=area).select_related('product', 'product__category')
    
    # Enrich needs for template
    enriched_needs = []
    for need in area_needs:
        enriched_needs.append({
            'need': need,
            'product': need.product,
            'category': need.product.category if need.product else None,
        })
    
    context = {
        'needs': enriched_needs,
        'products': Product.objects.select_related('category'),
        'areas': [area],
    }
    return render(request, 'area_admin/needs.html', context)


@login_required
def area_admin_categories(request):
    """View categories"""
    if request.user.user_type != 'area_admin':
        return redirect('login')
    
    context = {
        'categories': Category.objects.all(),
    }
    return render(request, 'area_admin/categories.html', context)


@login_required
def area_admin_products(request):
    """View products"""
    if request.user.user_type != 'area_admin':
        return redirect('login')
    
    products = Product.objects.select_related('category')
    
    context = {
        'products': products,
        'categories': Category.objects.all(),
    }
    return render(request, 'area_admin/products.html', context)


# Super Admin Views
@login_required
def super_admin_dashboard(request):
    """Dashboard for Super Admin"""
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied. Please login as Super Admin.')
        return redirect('login')
    
    stats = get_statistics()
    
    # Get all needs with area and product info
    all_needs = Need.objects.select_related('product', 'area', 'product__category').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'areas': Area.objects.all(),
        'needs': all_needs,
        'total_area_admins': AreaAdmin.objects.filter(is_active=True).count(),
    }
    return render(request, 'super_admin/dashboard.html', context)


@login_required
def super_admin_areas(request):
    """Manage areas"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Handle POST request to create/update area
    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        
        try:
            if area_id:  # Update existing
                area = Area.objects.get(id=area_id)
                area.name = name
                area.description = description
                area.address = address
                area.pincode = pincode
                area.save()
                messages.success(request, f'Area "{name}" updated successfully!')
            else:  # Create new
                area = Area.objects.create(
                    name=name,
                    description=description,
                    address=address,
                    pincode=pincode
                )
                messages.success(request, f'Area "{name}" created successfully!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('super_admin_areas')
    
    areas = Area.objects.annotate(needs_count=Count('needs')).order_by('name')
    
    context = {
        'areas': areas,
    }
    return render(request, 'super_admin/areas.html', context)


@login_required
def super_admin_area_admins(request):
    """Manage area admins"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Handle POST request to create/update area admin
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        area_id = request.POST.get('area')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            area = Area.objects.get(id=area_id)
            
            if admin_id:  # Update existing
                area_admin = AreaAdmin.objects.get(id=admin_id)
                area_admin.name = name
                area_admin.email = email
                area_admin.area = area
                area_admin.save()
                
                # Update user if password provided
                if password:
                    user = area_admin.user
                    user.set_password(password)
                    user.save()
                
                messages.success(request, f'Shelter admin "{name}" updated successfully!')
            else:  # Create new
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    user_type='area_admin',
                    first_name=name.split()[0] if ' ' in name else name,
                    last_name=name.split()[-1] if ' ' in name and len(name.split()) > 1 else '',
                    is_staff=True
                )
                
                # Create area admin profile
                area_admin = AreaAdmin.objects.create(
                    user=user,
                    name=name,
                    email=email,
                    area=area
                )
                
                messages.success(request, f'Shelter admin "{name}" created successfully!')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    area_admins = AreaAdmin.objects.select_related('area', 'user').filter(is_active=True)
    areas = Area.objects.all()
    
    # Convert to template-friendly format
    admins_list = []
    for admin in area_admins:
        admins_list.append({
            'admin': admin,
            'area': admin.area,
        })
    
    context = {
        'admins': admins_list,
        'areas': areas,
    }
    return render(request, 'super_admin/area_admins.html', context)


@login_required
def super_admin_all_needs(request):
    """View all needs across all areas with add functionality"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Handle POST request to create new need
    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        priority = request.POST.get('priority', 'medium')
        notes = request.POST.get('notes', '')
        
        try:
            area = Area.objects.get(id=area_id)
            product = Product.objects.get(id=product_id)
            
            need = Need.objects.create(
                area=area,
                product=product,
                quantity=int(quantity),
                priority=priority,
                notes=notes,
                created_by=request.user,
                status='pending'
            )
            messages.success(request, f'Need for {product.name} in {area.name} added successfully!')
        except Area.DoesNotExist:
            messages.error(request, 'Selected area not found')
        except Product.DoesNotExist:
            messages.error(request, 'Selected product not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('super_admin_all_needs')
    
    all_needs = Need.objects.select_related('product', 'area', 'product__category').order_by('-created_at')
    
    # Enrich needs for template
    enriched_needs = []
    for need in all_needs:
        enriched_needs.append({
            'need': need,
            'area': need.area,
            'product': need.product,
            'category': need.product.category if need.product else None,
        })
    
    context = {
        'needs': enriched_needs,
        'areas': Area.objects.all(),
        'products': Product.objects.select_related('category'),
        'categories': Category.objects.all(),
    }
    return render(request, 'super_admin/all_needs.html', context)


@login_required
def super_admin_categories(request):
    """Manage categories for super admin"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Handle POST request to create/update category
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        try:
            if category_id:  # Update existing
                category = Category.objects.get(id=category_id)
                category.name = name
                category.description = description
                category.save()
                messages.success(request, f'Category "{name}" updated successfully!')
            else:  # Create new
                category = Category.objects.create(
                    name=name,
                    description=description
                )
                messages.success(request, f'Category "{name}" created successfully!')
        except Category.DoesNotExist:
            messages.error(request, 'Category not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('super_admin_categories')
    
    categories = Category.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'super_admin/categories.html', context)


@login_required
def super_admin_products(request):
    """Manage products for super admin"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Handle POST request to create/update product
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category_id')
        unit = request.POST.get('unit', '')
        
        try:
            category = Category.objects.get(id=category_id)
            
            if product_id:  # Update existing
                product = Product.objects.get(id=product_id)
                product.name = name
                product.description = description
                product.category = category
                product.unit = unit
                product.save()
                messages.success(request, f'Product "{name}" updated successfully!')
            else:  # Create new
                product = Product.objects.create(
                    name=name,
                    description=description,
                    category=category,
                    unit=unit
                )
                messages.success(request, f'Product "{name}" created successfully!')
        except Category.DoesNotExist:
            messages.error(request, 'Selected category not found')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('super_admin_products')
    
    products = Product.objects.select_related('category').all().order_by('name')
    categories = Category.objects.all().order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'super_admin/products.html', context)


@login_required
@require_http_methods(["POST"])
def delete_product(request, product_id):
    """Delete a product"""
    if request.user.user_type != 'super_admin':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        messages.error(request, 'Access denied')
        return redirect('super_admin_products')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Product deleted successfully'})
        
        return redirect('super_admin_products')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Error: {str(e)}')
        return redirect('super_admin_products')


@login_required
def view_need_detail(request, need_id):
    """View detailed information about a specific need"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    need = get_object_or_404(Need.objects.select_related('product', 'area', 'product__category', 'created_by'), id=need_id)
    
    context = {
        'need': need,
        'product': need.product,
        'area': need.area,
        'category': need.product.category if need.product else None,
    }
    return render(request, 'super_admin/need_detail.html', context)


@login_required
@require_http_methods(["POST"])
def delete_category(request, category_id):
    """Delete a category"""
    if request.user.user_type != 'super_admin':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        messages.error(request, 'Access denied')
        return redirect('super_admin_categories')
    
    try:
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Category deleted successfully'})
        
        return redirect('super_admin_categories')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Error: {str(e)}')
        return redirect('super_admin_categories')


@login_required
@require_http_methods(["POST"])
def delete_area(request, area_id):
    """Delete an area"""
    if request.user.user_type != 'super_admin':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        messages.error(request, 'Access denied')
        return redirect('super_admin_areas')
    
    try:
        area = get_object_or_404(Area, id=area_id)
        area_name = area.name
        area.delete()
        messages.success(request, f'Area "{area_name}" deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Area deleted successfully'})
        
        return redirect('super_admin_areas')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Error: {str(e)}')
        return redirect('super_admin_areas')


@login_required
@require_http_methods(["POST"])
def delete_area_admin(request, admin_id):
    """Delete an area admin"""
    if request.user.user_type != 'super_admin':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        messages.error(request, 'Access denied')
        return redirect('super_admin_area_admins')
    
    try:
        area_admin = get_object_or_404(AreaAdmin, id=admin_id)
        admin_name = area_admin.name
        # Delete associated user as well
        user = area_admin.user
        area_admin.delete()
        user.delete()
        messages.success(request, f'Area admin "{admin_name}" deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Area admin deleted successfully'})
        
        return redirect('super_admin_area_admins')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Error: {str(e)}')
        return redirect('super_admin_area_admins')


@login_required
@require_http_methods(["POST"])
def delete_contact(request, contact_id):
    """Delete a contact message"""
    if request.user.user_type != 'super_admin':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        messages.error(request, 'Access denied')
        return redirect('super_admin_contacts')
    
    try:
        contact = get_object_or_404(Contact, id=contact_id)
        contact_name = contact.name
        contact.delete()
        messages.success(request, f'Contact message from "{contact_name}" deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Contact deleted successfully'})
        
        return redirect('super_admin_contacts')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Error: {str(e)}')
        return redirect('super_admin_contacts')


@login_required
@require_http_methods(["POST"])
def delete_need(request, need_id):
    """Delete a need"""
    if request.user.user_type != 'super_admin':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
        messages.error(request, 'Access denied')
        return redirect('super_admin_all_needs')
    
    try:
        need = get_object_or_404(Need, id=need_id)
        product_name = need.product.name
        area_name = need.area.name
        need.delete()
        messages.success(request, f'Need for {product_name} in {area_name} deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Need deleted successfully'})
        
        return redirect('super_admin_all_needs')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Error: {str(e)}')
        return redirect('super_admin_all_needs')


@login_required
def export_needs(request, format):
    """Export needs data in various formats"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Get all needs
    needs = Need.objects.select_related('product', 'area', 'product__category').order_by('-created_at')
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="relief_needs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Area', 'Product', 'Category', 'Unit', 'Quantity', 'Priority', 'Status', 'Notes', 'Created At'])
        
        for need in needs:
            writer.writerow([
                need.id,
                need.area.name,
                need.product.name,
                need.product.category.name if need.product.category else '',
                need.product.unit,
                need.quantity,
                need.get_priority_display(),
                need.get_status_display(),
                need.notes or '',
                need.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    elif format == 'excel':
        # For Excel, we'll use CSV format with .xls extension (simple approach)
        # For proper Excel, you'd need openpyxl library
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="relief_needs.xls"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Area', 'Product', 'Category', 'Unit', 'Quantity', 'Priority', 'Status', 'Notes', 'Created At'])
        
        for need in needs:
            writer.writerow([
                need.id,
                need.area.name,
                need.product.name,
                need.product.category.name if need.product.category else '',
                need.product.unit,
                need.quantity,
                need.get_priority_display(),
                need.get_status_display(),
                need.notes or '',
                need.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    elif format == 'pdf':
        # For PDF, we'll return a simple HTML that can be printed as PDF
        # For proper PDF, you'd need reportlab or weasyprint library
        from django.template.loader import render_to_string
        
        context = {
            'needs': needs,
            'export_date': timezone.now() if hasattr(timezone, 'now') else None,
        }
        
        html_content = render_to_string('super_admin/export_pdf.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relief_needs.pdf"'
        response.write(html_content)
        
        return response
    
    else:
        messages.error(request, 'Invalid export format')
        return redirect('super_admin_all_needs')


@login_required
def super_admin_contacts(request):
    """View all contact form submissions for super admin"""
    if request.user.user_type != 'super_admin':
        return redirect('login')
    
    # Handle status update
    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        new_status = request.POST.get('status')
        
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.status = new_status
            contact.save()
            messages.success(request, 'Contact status updated successfully!')
        except Contact.DoesNotExist:
            messages.error(request, 'Contact not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('super_admin_contacts')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    contacts = Contact.objects.all()
    
    # Apply filters
    if status_filter:
        contacts = contacts.filter(status=status_filter)
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    contacts = contacts.order_by('-created_at')
    
    context = {
        'contacts': contacts,
        'selected_status': status_filter,
        'search_query': search_query,
        'total_contacts': contacts.count(),
        'new_contacts': Contact.objects.filter(status='new').count(),
    }
    return render(request, 'super_admin/contacts.html', context)


@login_required
def database_management(request):
    """Database management page for Super Admin"""
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied. Please login as Super Admin.')
        return redirect('login')
    
    # Get database file info
    db_path = settings.DATABASES['default']['NAME']
    # Convert Path object to string if needed
    if isinstance(db_path, Path):
        db_path = str(db_path)
    db_size = 0
    db_modified = None
    
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        db_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
    
    context = {
        'db_path': db_path,
        'db_size': db_size,
        'db_size_mb': round(db_size / (1024 * 1024), 2),
        'db_modified': db_modified,
    }
    return render(request, 'super_admin/database.html', context)


@login_required
def export_database(request):
    """Export database to SQL file"""
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied. Please login as Super Admin.')
        return redirect('login')
    
    try:
        db_path = settings.DATABASES['default']['NAME']
        # Convert Path object to string if needed
        if isinstance(db_path, Path):
            db_path = str(db_path)
        
        if not os.path.exists(db_path):
            messages.error(request, 'Database file not found!')
            return redirect('database_management')
        
        # Create backup file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.sql'
        backup_path = BASE_DIR / backup_filename
        
        # Connect and dump
        conn = sqlite3.connect(db_path)
        with open(backup_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        conn.close()
        
        # Create HTTP response with file
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup_filename}"'
        
        # Optionally delete the file after sending (or keep it)
        # os.remove(backup_path)
        
        messages.success(request, f'Database exported successfully! File: {backup_filename}')
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting database: {str(e)}')
        return redirect('database_management')


@login_required
def import_database(request):
    """Import database from SQL file"""
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied. Please login as Super Admin.')
        return redirect('login')
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('database_management')
    
    try:
        # Check if file was uploaded
        if 'sql_file' not in request.FILES:
            messages.error(request, 'No file uploaded!')
            return redirect('database_management')
        
        uploaded_file = request.FILES['sql_file']
        
        # Validate file extension
        if not uploaded_file.name.endswith('.sql'):
            messages.error(request, 'Invalid file format! Please upload a .sql file.')
            return redirect('database_management')
        
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        
        # Get database path
        db_path = settings.DATABASES['default']['NAME']
        # Convert Path object to string if needed
        if isinstance(db_path, Path):
            db_path = str(db_path)
        
        # Create backup before import (safety measure)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_backup = f'safety_backup_{timestamp}.sql'
        safety_backup_path = BASE_DIR / safety_backup
        
        if os.path.exists(db_path):
            conn_backup = sqlite3.connect(db_path)
            with open(safety_backup_path, 'w', encoding='utf-8') as f:
                for line in conn_backup.iterdump():
                    f.write('%s\n' % line)
            conn_backup.close()
        
        # Connect to database and execute SQL
        conn = sqlite3.connect(db_path)
        conn.executescript(file_content)
        conn.close()
        
        messages.success(request, f'Database imported successfully! A safety backup was created: {safety_backup}')
        return redirect('database_management')
        
    except sqlite3.Error as e:
        messages.error(request, f'Database error: {str(e)}')
        return redirect('database_management')
    except Exception as e:
        messages.error(request, f'Error importing database: {str(e)}')
        return redirect('database_management')
