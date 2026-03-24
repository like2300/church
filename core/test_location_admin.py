#!/usr/bin/env python
"""Test script to check if map appears in admin page"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create client and login
client = Client(SERVER_NAME='127.0.0.1', SERVER_PORT='8000')

# Ensure superuser exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@church.com', 'admin123')
    print("Created superuser: admin / admin123")

# Login
logged_in = client.login(username='admin', password='admin123')
print(f"Logged in: {logged_in}")

# Test the location change page
print("\nFetching /admin/church/location/1/change/...")
response = client.get('http://127.0.0.1:8000/admin/church/location/1/change/')
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.content)} bytes")

content = response.content.decode('utf-8', errors='ignore')

# Check for map content
checks = {
    'Carte Interactive': 'Carte Interactive' in content,
    'id="map"': 'id="map"' in content,
    'location_map': 'location_map' in content,
    'leaflet.css': 'leaflet.css' in content,
    'leaflet.js': 'leaflet.js' in content,
    'initMap': 'initMap' in content,
    'form_before': 'form_before' in content,
}

print("\n" + "=" * 60)
print("Content Checks")
print("=" * 60)
for check, found in checks.items():
    status = "✅" if found else "❌"
    print(f"{status} {check}: {found}")

# Save HTML for debugging
with open('/tmp/admin_location.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\nFull HTML saved to: /tmp/admin_location.html")

# Show relevant parts
if 'id="map"' not in content:
    print("\nSearching for map-related content...")
    import re
    # Look for any div with map in name
    maps = re.findall(r'<div[^>]*map[^>]*>', content, re.IGNORECASE)
    if maps:
        print("Found divs with 'map':")
        for m in maps[:5]:
            print(f"  {m[:100]}")
    else:
        print("No div with 'map' found")
