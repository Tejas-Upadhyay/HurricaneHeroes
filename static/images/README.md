# Logo Setup Instructions

## Logo File Location

Please place your Hurricane Heroes logo file in this directory:
- **File name**: `logo.png`
- **Full path**: `static/images/logo.png`

## Logo Specifications

The logo should be:
- **Format**: PNG (with transparent background preferred)
- **Size**: Recommended 200x200px or higher (will be resized to 40x40px in navbar)
- **Name**: Must be exactly `logo.png`

## Current Usage

The logo is used in:
1. **Navbar** - All pages (Public, Super Admin, Area Admin)
2. **Favicon** - Browser tab icon
3. **Brand identity** - Throughout the application

## After Adding Logo

1. Place `logo.png` in this `static/images/` folder
2. Run `python manage.py collectstatic` (if in production)
3. Refresh your browser to see the logo

## Alternative Formats

If you have the logo in a different format:
- `.jpg` or `.jpeg` - Convert to PNG for better quality
- `.svg` - Can be used but update template references from `logo.png` to `logo.svg`
- `.ico` - Can be used for favicon specifically

