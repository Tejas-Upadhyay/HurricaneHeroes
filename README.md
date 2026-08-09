# Hurricane Heroes 🌀

A web application to coordinate hurricane relief efforts across Southwest Florida shelters. Built with Django, it connects donors and volunteers with shelters that need help.

## Live Site
**https://southwestfloridahurricaneheroes.com/**

## Features

### Public Pages
- **Homepage** — Live stats, current needs, and quick access to all features
- **Interactive Shelter Map** — Leaflet.js map with all 20+ shelter locations
- **Regions** — Browse shelters as cards with addresses and zip codes
- **Volunteer Sign Up** — Registration form for community volunteers
- **Request Help** — Public form for affected people to request relief items
- **Donate** — Log donations and view recent community contributions
- **Global Search** — Search across shelters, products, and needs
- **Weather Alerts** — Live NOAA alerts for Lee County displayed as banner
- **English/Spanish Toggle** — Basic multilingual navigation support

### Area Admin Panel
- Dashboard with area-specific stats
- Manage relief needs (add, edit, delete)
- View categories and products
- Filter and sort capabilities

### Super Admin Panel
- Dashboard with charts (Chart.js) — needs by priority, category, shelter, status
- Manage regions, shelter admins, categories, products
- View all needs across all shelters
- Manage volunteers, donations, need requests, and contact messages
- Database import/export
- Mobile-friendly sidebar

## Technology Stack

- **Backend**: Django 5.0+ (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5.3
- **Database**: SQLite3
- **Maps**: Leaflet.js + OpenStreetMap
- **Charts**: Chart.js
- **Icons**: Font Awesome 6.4
- **Weather**: NOAA Weather API
- **Geocoding**: OpenStreetMap Nominatim

## Installation

### Prerequisites
- Python 3.8+

### Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py populate_data    # Load sample data (optional)
python manage.py geocode_shelters # Add map coordinates to shelters
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

## Login Credentials

After running `populate_data`:
- **Super Admin**: username `super_admin`, password `admin123`
- **Area Admins**: username `area_admin_1`, password `admin123`

Or create your own:
```bash
python manage.py createsuperuser
```

## Project Structure

```
HurricaneHeroes/
├── relief_system/          # Django settings and config
├── relief_app/             # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin config
│   └── management/         # Custom management commands
├── templates/              # HTML templates
│   ├── base.html           # Base layout
│   ├── 404.html            # Custom error page
│   ├── 500.html            # Custom error page
│   ├── public/             # Public-facing pages
│   ├── area_admin/         # Area admin panel
│   ├── super_admin/        # Super admin panel
│   └── auth/               # Login page
├── static/                 # CSS, images
├── db.sqlite3              # SQLite database
├── manage.py
└── requirements.txt
```

## Deployment

Currently deployed on **Azure App Service**. See `AZURE_DEPLOYMENT_GUIDE.md` for details.

## License

Created for educational purposes — Southwest Florida Hurricane Relief Project.
