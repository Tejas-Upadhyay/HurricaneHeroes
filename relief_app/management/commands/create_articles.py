"""
Create starter blog articles for SEO
"""
from django.core.management.base import BaseCommand
from relief_app.models import Article


class Command(BaseCommand):
    help = 'Create starter blog articles for SEO'

    def handle(self, *args, **options):
        articles = [
            {
                'title': 'How to Prepare for a Hurricane in Southwest Florida',
                'slug': 'how-to-prepare-for-hurricane-southwest-florida',
                'summary': 'Essential preparation tips for Southwest Florida residents before hurricane season hits. Learn what supplies to stock, how to protect your home, and where to find shelter.',
                'content': """Hurricane season in Southwest Florida runs from June 1 to November 30. Being prepared can save lives and reduce damage. Here is a comprehensive guide for SWFL residents.

Build Your Emergency Kit

Every household should have supplies for at least 72 hours:
- Water: 1 gallon per person per day for at least 3 days
- Non-perishable food: canned goods, energy bars, dried fruit
- Medications: at least a 7-day supply of prescriptions
- First aid kit with bandages, antiseptic, and pain relievers
- Flashlights and extra batteries
- Battery-powered or hand-crank radio
- Important documents in waterproof container
- Cash in small bills
- Phone chargers and portable battery packs

Protect Your Home

- Install hurricane shutters or pre-cut plywood for windows
- Trim trees and remove dead branches
- Secure outdoor furniture, grills, and decorations
- Know how to turn off utilities (gas, water, electricity)
- Check your roof for loose shingles or tiles
- Clear gutters and drains

Know Your Evacuation Zone

Lee County has evacuation zones A through E. Know which zone you live in and have a plan for where you will go. Visit the Lee County Emergency Management website to find your zone.

Find Your Nearest Shelter

Hurricane Heroes provides real-time information on shelter locations and what they need. Visit our Regions page or interactive Map to find shelters near you.

Stay Informed

- Sign up for Lee County emergency alerts
- Download the FEMA app
- Follow local news and the National Hurricane Center
- Monitor Hurricane Heroes for shelter needs and updates

After the Storm

- Do not return home until authorities say it is safe
- Watch for downed power lines and flooding
- Document damage with photos for insurance
- Check on neighbors, especially elderly and disabled
- Visit Hurricane Heroes to see how you can help shelters in need"""
            },
            {
                'title': 'What Supplies Do Hurricane Shelters Need Most',
                'slug': 'what-supplies-hurricane-shelters-need-most',
                'summary': 'A guide for donors who want to help hurricane shelters in Southwest Florida. Learn which items are always in high demand during and after storms.',
                'content': """When a hurricane hits Southwest Florida, shelters quickly fill up and supplies run low. If you want to help, here are the items that shelters need most.

Water and Hydration

Water is always the number one need. Shelters go through thousands of bottles during a hurricane event.
- Bottled water (cases)
- Electrolyte drinks
- Water purification tablets

Food

Non-perishable items that are easy to distribute:
- Canned goods (with pull-tab lids)
- Peanut butter and crackers
- Granola bars and energy bars
- Shelf-stable milk
- Baby formula and baby food
- Snacks for children

Hygiene and Personal Care

- Toilet paper
- Hand sanitizer
- Soap and shampoo
- Toothbrushes and toothpaste
- Diapers and wipes
- Feminine hygiene products
- Deodorant

Bedding and Comfort

- Blankets and sheets
- Pillows
- Air mattresses
- Sleeping bags
- Towels

Medical Supplies

- First aid kits
- Over-the-counter pain relievers
- Band-aids and gauze
- Prescription medication (donated through proper channels)
- Hand sanitizer

Clothing

- Socks and underwear (new)
- T-shirts
- Shorts and pants
- Rain ponchos
- Shoes and sandals

How to Donate

Visit Hurricane Heroes to see exactly what each shelter needs right now. Our platform shows real-time needs updated by shelter administrators. You can also log your donations on our Donate page to help us track community contributions.

Remember: check the specific needs of your local shelter before donating. Shelters may already have plenty of some items and desperately need others."""
            },
            {
                'title': 'How Hurricane Heroes Helps Southwest Florida Communities',
                'slug': 'how-hurricane-heroes-helps-southwest-florida',
                'summary': 'Learn how Hurricane Heroes, created by an Estero High School student, connects donors and volunteers with hurricane shelters across Lee County.',
                'content': """Hurricane Heroes is a free community platform created by an Estero High School student to help Southwest Florida recover faster from hurricanes.

The Problem We Solve

During hurricanes, there is a disconnect between people who want to help and shelters that need help. Generous community members often do not know what specific items shelters need. Meanwhile, shelters struggle to communicate their urgent requirements to the public.

Hurricane Heroes bridges this gap with technology.

How It Works

For Donors:
Visit our website to see real-time needs at 20+ shelters across Lee County. Filter by region, category, or priority to find where your help is needed most. After donating, log your contribution on our platform.

For Volunteers:
Sign up through our volunteer registration page. Tell us your skills, availability, and preferred shelter location. When a hurricane approaches or hits, our team coordinates volunteer efforts.

For Those In Need:
Submit a help request through our Request Help page. Tell us what you need, how urgently, and your nearest shelter. Our team reviews requests and works to fulfill them.

For Shelter Administrators:
Each shelter has a dedicated admin who updates needs in real time. This ensures the community always sees accurate, current information.

Our Coverage

Hurricane Heroes currently serves 20+ shelter locations across Southwest Florida including:
- Fort Myers
- Cape Coral
- Estero
- Lehigh Acres
- North Fort Myers
- Bonita Springs

Features

- Interactive shelter map with all locations
- Real-time needs tracking
- Volunteer registration
- Donation logging and tracking
- Public need request form
- Weather alerts from NOAA
- Multi-language support

Join the Community

Whether you can donate supplies, volunteer your time, or simply share our website with others, every action helps. Together, we can ensure no shelter goes without essential supplies during hurricane season.

Visit southwestfloridahurricaneheroes.com to get started."""
            },
        ]

        created = 0
        for data in articles:
            article, was_created = Article.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {data["title"]}'))
            else:
                self.stdout.write(f'  - Already exists: {data["title"]}')

        self.stdout.write(self.style.SUCCESS(f'\nDone! {created} articles created.'))
