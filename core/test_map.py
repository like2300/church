#!/usr/bin/env python
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

# Create client and login
client = Client()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@church.com", "admin123")

client.login(username="admin", password="admin123")

# Test the location change page
response = client.get("/admin/church/location/1/change/")
content = response.content.decode()

if "Carte Interactive" in content or "location_map" in content or 'id="map"' in content:
    print("✅ MAP TEMPLATE IS LOADED!")
    if 'id="map"' in content:
        print("✅ Map div found")
    if "leaflet" in content.lower():
        print("✅ Leaflet CSS/JS found")
    if "initMap" in content:
        print("✅ initMap function found")
else:
    print("❌ Map template NOT loaded")
    print("\nLooking for template usage...")
    if "change_form" in content:
        print("- change_form template found")

# Save HTML for debugging
with open("/tmp/admin_page.html", "w") as f:
    f.write(content)
print(f"\nPage saved to /tmp/admin_page.html ({len(content)} bytes)")


"""
- admin / admin123 → Sélectionnez Paroisse de Talangaï (Brazzaville)
        - agent_brazza / agent123 → Sélectionnez Église Centrale de Brazzaville
        - agent_pointe / agent123 → Sélectionnez Église de Pointe-Noire Centre
        - agent_dolisie / agent123 → Sélectionnez Église de Dolisie
"""
