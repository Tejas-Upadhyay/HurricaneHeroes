"""
Management command to populate initial data for Hurricane Heroes Relief System
Run with: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from relief_app.models import Category, Area, Product, AreaAdmin, Need

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Clear existing data (optional - comment out if you want to keep data)
        self.stdout.write('Clearing existing data...')
        Need.objects.all().delete()
        AreaAdmin.objects.all().delete()
        Product.objects.all().delete()
        Area.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))
        
        # Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'id': 1, 'name': 'Food', 'description': 'Food and nutrition supplies'},
            {'id': 2, 'name': 'Medicine', 'description': 'Medical supplies and medicines'},
            {'id': 3, 'name': 'Shelter', 'description': 'Temporary shelter and tents'},
            {'id': 4, 'name': 'Clothing', 'description': 'Clothes and personal items'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories[cat_data['id']] = category
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        
        # Create Areas
        self.stdout.write('Creating areas...')
        areas_data = [
            {'id': 1, 'name': 'Mumbai District', 'description': 'Mumbai metropolitan area', 
             'address': 'Mumbai, Maharashtra, India', 'pincode': '400001'},
            {'id': 2, 'name': 'Pune District', 'description': 'Pune city and surrounding areas', 
             'address': 'Pune, Maharashtra, India', 'pincode': '411001'},
            {'id': 3, 'name': 'Delhi District', 'description': 'Delhi NCR region', 
             'address': 'New Delhi, Delhi, India', 'pincode': '110001'},
        ]
        
        areas = {}
        for area_data in areas_data:
            area = Area.objects.create(**area_data)
            areas[area_data['id']] = area
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(areas)} areas'))
        
        # Create Products
        self.stdout.write('Creating products...')
        products_data = [
            {'id': 1, 'name': 'Rice', 'description': 'Basmati rice', 'category': categories[1], 'unit': 'kg'},
            {'id': 2, 'name': 'Wheat Flour', 'description': 'Wheat flour', 'category': categories[1], 'unit': 'kg'},
            {'id': 3, 'name': 'Biscuits', 'description': 'Dry biscuits', 'category': categories[1], 'unit': 'packets'},
            {'id': 4, 'name': 'Pain Relievers', 'description': 'Pain relief medicines', 'category': categories[2], 'unit': 'boxes'},
            {'id': 5, 'name': 'Antibiotics', 'description': 'Antibiotic medicines', 'category': categories[2], 'unit': 'strips'},
            {'id': 6, 'name': 'First Aid Kit', 'description': 'Complete first aid kit', 'category': categories[2], 'unit': 'kits'},
            {'id': 7, 'name': 'Tents', 'description': 'Temporary shelter tents', 'category': categories[3], 'unit': 'units'},
            {'id': 8, 'name': 'Tarpaulin', 'description': 'Tarpaulin sheets', 'category': categories[3], 'unit': 'meters'},
            {'id': 9, 'name': 'Blankets', 'description': 'Warm blankets', 'category': categories[3], 'unit': 'pieces'},
            {'id': 10, 'name': 'Clothes', 'description': 'Used clothes', 'category': categories[4], 'unit': 'pieces'},
            {'id': 11, 'name': 'Shoes', 'description': 'Footwear', 'category': categories[4], 'unit': 'pairs'},
        ]
        
        products = {}
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            products[product_data['id']] = product
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        
        # Create Super Admin User
        self.stdout.write('Creating super admin user...')
        super_admin = User.objects.create_user(
            username='super_admin',
            email='admin@relief.com',
            password='admin123',
            user_type='super_admin',
            first_name='Super',
            last_name='Admin',
            is_staff=True,
            is_superuser=True
        )
        self.stdout.write(self.style.SUCCESS('Created super admin user'))
        
        # Create Area Admin Users
        self.stdout.write('Creating area admin users...')
        area_admins_data = [
            {'name': 'Rajesh Kumar', 'email': 'rajesh@relief.com', 'area': areas[1]},
            {'name': 'Priya Sharma', 'email': 'priya@relief.com', 'area': areas[2]},
            {'name': 'Amit Patel', 'email': 'amit@relief.com', 'area': areas[3]},
        ]
        
        area_admins_created = []
        for i, admin_data in enumerate(area_admins_data, 1):
            user = User.objects.create_user(
                username=f'area_admin_{i}',
                email=admin_data['email'],
                password='admin123',
                user_type='area_admin',
                first_name=admin_data['name'].split()[0],
                last_name=admin_data['name'].split()[-1],
                is_staff=True
            )
            area_admin = AreaAdmin.objects.create(
                user=user,
                name=admin_data['name'],
                email=admin_data['email'],
                area=admin_data['area']
            )
            area_admins_created.append(area_admin)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(area_admins_created)} area admins'))
        
        # Create Needs
        self.stdout.write('Creating needs...')
        needs_data = [
            {'area': areas[1], 'product': products[1], 'quantity': 5000, 'notes': 'Urgent need', 'priority': 'urgent'},
            {'area': areas[1], 'product': products[4], 'quantity': 200, 'notes': '', 'priority': 'medium'},
            {'area': areas[1], 'product': products[7], 'quantity': 150, 'notes': 'High priority', 'priority': 'high'},
            {'area': areas[1], 'product': products[10], 'quantity': 500, 'notes': '', 'priority': 'medium'},
            {'area': areas[2], 'product': products[2], 'quantity': 3000, 'notes': '', 'priority': 'medium'},
            {'area': areas[2], 'product': products[3], 'quantity': 1000, 'notes': 'Dry food needed', 'priority': 'high'},
            {'area': areas[2], 'product': products[5], 'quantity': 300, 'notes': '', 'priority': 'medium'},
            {'area': areas[2], 'product': products[8], 'quantity': 5000, 'notes': 'Coverage material', 'priority': 'high'},
            {'area': areas[3], 'product': products[1], 'quantity': 8000, 'notes': 'Large requirement', 'priority': 'urgent'},
            {'area': areas[3], 'product': products[6], 'quantity': 500, 'notes': '', 'priority': 'medium'},
            {'area': areas[3], 'product': products[9], 'quantity': 2000, 'notes': 'Winter season', 'priority': 'high'},
            {'area': areas[3], 'product': products[11], 'quantity': 1000, 'notes': '', 'priority': 'medium'},
        ]
        
        for need_data in needs_data:
            Need.objects.create(**need_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(needs_data)} needs'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('\nLogin Credentials:'))
        self.stdout.write(self.style.SUCCESS('Super Admin: username=super_admin, password=admin123'))
        self.stdout.write(self.style.SUCCESS('Area Admin 1: username=area_admin_1, password=admin123'))
        self.stdout.write(self.style.SUCCESS('Area Admin 2: username=area_admin_2, password=admin123'))
        self.stdout.write(self.style.SUCCESS('Area Admin 3: username=area_admin_3, password=admin123'))

