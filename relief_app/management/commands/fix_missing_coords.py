"""
Fix coordinates for shelters that failed geocoding.
Hardcoded lat/lng for the 7 known locations.
"""
from django.core.management.base import BaseCommand
from relief_app.models import Area


class Command(BaseCommand):
    help = 'Set coordinates for shelters that failed geocoding'

    def handle(self, *args, **options):
        # Known coordinates for the 7 missing shelters
        fixes = {
            'Alico Arena': (26.4645, -81.7709),
            'Gateway High School': (26.5732, -81.7475),
            'Island Coast High School': (26.6088, -81.9498),
            'Manatee Elementary': (26.6388, -81.8133),
            'N. Fort Myers Academy of the Arts': (26.7200, -81.8650),
            'North Fort Myers Recreation Center': (26.7150, -81.8580),
            'Oak Hammock Middle School': (26.6400, -81.8130),
        }

        updated = 0
        for name, (lat, lng) in fixes.items():
            try:
                area = Area.objects.get(name=name)
                area.latitude = lat
                area.longitude = lng
                area.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ {name}: {lat}, {lng}'))
                updated += 1
            except Area.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ✗ {name}: Not found in database'))

        self.stdout.write(self.style.SUCCESS(f'\nDone! Updated {updated} shelters.'))
        
        # Show final count
        total = Area.objects.count()
        with_coords = Area.objects.filter(latitude__isnull=False).count()
        self.stdout.write(self.style.SUCCESS(f'{with_coords}/{total} shelters now have coordinates.'))
