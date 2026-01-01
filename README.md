# Hurricane Heroes

A comprehensive web-based application designed to efficiently manage and coordinate hurricane relief efforts across different geographical areas.

## Features

### 🎯 Three Main Panels

1. **Public/Front Panel** - Public access to view relief needs
2. **Area Admin Panel** - Manage relief needs for assigned area
3. **Super Admin Panel** - Complete system oversight and management

### 🚀 Key Features

- **No Database Required** - Uses static data for design demonstration
- **Responsive Design** - Bootstrap 5 with modern UI
- **Role-Based Access** - Different dashboards for different user roles
- **Real-time Statistics** - Dashboard with key metrics
- **Area Management** - Track needs across multiple geographical areas
- **Product Categories** - Organize relief items by categories (Food, Medicine, Shelter, Clothing)
- **Need Tracking** - Monitor relief requirements with quantities and notes

## Technology Stack

- **Framework**: Django 5.0+
- **Frontend**: HTML5, CSS3, Bootstrap 5.3
- **Icons**: Font Awesome 6.4
- **Database**: Static data (no database connectivity)

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone or extract the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   python manage.py runserver
   ```

4. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000/`

## Usage

### Public Access

1. Visit `http://127.0.0.1:8000/` to view the public homepage
2. Browse areas and view relief needs
3. No login required

### Area Admin Access

1. Click "Login" in the navigation
2. Enter any username and password
3. Select "Area Admin" as the role
4. Access the Area Admin Dashboard to manage relief needs

### Super Admin Access

1. Click "Login" in the navigation
2. Enter any username and password
3. Select "Super Admin" as the role
4. Access the Super Admin Dashboard for complete system management

## Project Structure

```
pythonpro/
├── relief_system/          # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── relief_app/             # Main application
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py
│   └── views.py
├── templates/              # HTML templates
│   ├── base.html
│   ├── auth/
│   │   └── login.html
│   ├── public/
│   │   ├── home.html
│   │   ├── areas.html
│   │   └── area_detail.html
│   ├── area_admin/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── needs.html
│   │   ├── categories.html
│   │   └── products.html
│   └── super_admin/
│       ├── base.html
│       ├── dashboard.html
│       ├── areas.html
│       ├── area_admins.html
│       └── all_needs.html
├── manage.py
├── requirements.txt
└── README.md
```

## Static Data

The system uses predefined static data for demonstration:

- **3 Areas**: Mumbai, Pune, Delhi
- **4 Categories**: Food, Medicine, Shelter, Clothing
- **11 Products**: Various relief items across categories
- **12 Needs**: Relief requirements across areas
- **3 Area Admins**: One for each area

## User Roles

### Super Admin
- View comprehensive dashboard
- Manage all areas
- Create and manage area admins
- View all needs across all areas
- System-wide analytics

### Area Admin
- View area-specific dashboard
- Update relief needs for assigned area
- View categories and products
- Track quantities needed

### Public Users
- View public homepage
- Browse all coverage areas
- View area-specific relief needs
- No login required

## Design Features

- Modern gradient-based color scheme
- Responsive cards and tables
- Interactive hover effects
- Font Awesome icons throughout
- Bootstrap modals for forms
- Clean and professional UI

## Important Notes

⚠️ **This is a design-only implementation**
- No actual database connectivity
- Login is simulated (any credentials work)
- Forms show but don't save data
- Perfect for UI/UX demonstration

## Future Enhancements

When implementing actual functionality:
1. Add database models
2. Implement real authentication
3. Add form processing
4. Enable CRUD operations
5. Add file uploads
6. Implement export features
7. Add advanced filtering
8. Create API endpoints

## Support

For questions or issues, please refer to the project documentation.

## License

This project is created for demonstration purposes.

