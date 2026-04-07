#!/usr/bin/env python
"""Direct test of Location admin with map"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.test import RequestFactory
from church.models import Location
from church.admin import LocationAdmin

# Get first location
location = Location.objects.first()
print(f"Testing with location: {location.name if location else 'None'}")

# Create admin instance
admin_site = LocationAdmin(Location, None)

# Create mock request
factory = RequestFactory()
request = factory.get('/admin/church/location/1/change/')

# Test the interactive_map method
html = admin_site.interactive_map(location)
print(f"\nMap HTML generated: {len(html)} bytes")
print(f"Contains 'location-map': {'location-map' in html}")
print(f"Contains 'leaflet': {'leaflet' in html.lower()}")
print(f"Contains 'congo_departments': {'congo_departments' in html}")

# Save to file for inspection
with open('/tmp/map_test.html', 'w') as f:
    f.write(html)
print("\nSaved to: /tmp/map_test.html")
