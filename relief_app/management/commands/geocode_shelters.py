"""
Management command to add coordinates to shelter locations.
Uses known addresses in Southwest Florida to set lat/lng.
"""
from django.core.management.base import BaseCommand
from relief_app.models import Area
import urllib.request
import json
import time


class Command(BaseCommand):
    help = 'Geocode shelter addresses using free Nominatim API'

    def handle(self, *args, **options):
        areas = Area.objects.filter(latitude__isnull=True)
        
        if not areas.exists():
            self.stdout.write(self.style.SUCCESS('All shelters already have coordinates!'))
            return
        
        self.stdout.write(f'Found {areas.count()} shelters without coordinates...')
        
        for area in areas:
            # Build search query from address
            query = f"{area.address}, FL {area.pincode}"
            encoded_query = query.replace(' ', '+').replace(',', '%2C')
            
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1"
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'HurricaneHeroes/1.0'})
                response = urllib.request.urlopen(req)
                data = json.loads(response.read())
                
                if data:
                    area.latitude = float(data[0]['lat'])
                    area.longitude = float(data[0]['lon'])
                    area.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {area.name}: {area.latitude}, {area.longitude}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ✗ {area.name}: No results found for "{query}"'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ {area.name}: Error - {str(e)}'
                ))
            
            # Be nice to the free API - wait 1 second between requests
            time.sleep(1)
        
        # Show summary
        geocoded = Area.objects.filter(latitude__isnull=False).count()
        total = Area.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\nDone! {geocoded}/{total} shelters have coordinates.'))
