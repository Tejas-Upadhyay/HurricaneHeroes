# Hurricane Heroes - Setup Instructions

## Quick Start Guide

### 1. Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
Open terminal/command prompt in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Application

#### On Windows:
```bash
python manage.py runserver
```
Or simply double-click `run.bat`

#### On Linux/Mac:
```bash
python manage.py runserver
```
Or make run.sh executable and run it:
```bash
chmod +x run.sh
./run.sh
```

### 4. Access the Application
Open your web browser and navigate to:
**http://127.0.0.1:8000/**

## Usage Guide

### Public Access (No Login Required)
- Visit the home page to view statistics and areas
- Browse coverage areas
- View area-specific relief needs

### Area Admin Access
1. Click "Login" button
2. Enter any username and password
3. Select "Area Admin" from role dropdown
4. Click "Login"
5. You'll be redirected to Area Admin Dashboard
6. View/Manage relief needs, categories, and products

### Super Admin Access
1. Click "Login" button
2. Enter any username and password
3. Select "Super Admin" from role dropdown
4. Click "Login"
5. You'll be redirected to Super Admin Dashboard
6. Access complete system overview, manage areas, and area admins

## Important Notes

⚠️ **This is a Design-Only Implementation**
- No database is used - all data is static
- Login is simulated - any username/password works
- Forms display but don't actually save data
- Perfect for UI/UX demonstration

## Pages Overview

### Public Pages
- `/` - Home page with statistics
- `/areas/` - List of all areas
- `/area/<id>/` - Area detail with needs

### Area Admin Pages
- `/area-admin/dashboard/` - Area Admin Dashboard
- `/area-admin/needs/` - Manage relief needs
- `/area-admin/categories/` - View categories
- `/area-admin/products/` - View products

### Super Admin Pages
- `/super-admin/dashboard/` - Super Admin Dashboard
- `/super-admin/areas/` - Manage areas
- `/super-admin/area-admins/` - Manage area administrators
- `/super-admin/all-needs/` - View all needs across all areas

## Design Features

- ✅ Modern, responsive Bootstrap 5 UI
- ✅ Three distinct panels (Public, Area Admin, Super Admin)
- ✅ Beautiful gradient color scheme
- ✅ Interactive cards and tables
- ✅ Font Awesome icons throughout
- ✅ Hover effects and animations
- ✅ Modal forms for data entry
- ✅ Statistics dashboard
- ✅ Professional sidebar navigation

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, specify a different port:
```bash
python manage.py runserver 8080
```

### Module Not Found Error
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Static Files Not Loading
This project uses CDN (Bootstrap and Font Awesome are loaded from the internet), so no static files collection is needed.

## Next Steps (For Actual Implementation)

When you're ready to add actual functionality:

1. Create database models in `relief_app/models.py`
2. Run migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Add real authentication system
5. Implement form processing
6. Add CRUD operations
7. Enable data persistence

Enjoy exploring the Hurricane Heroes design! 🎉

