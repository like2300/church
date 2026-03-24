#!/usr/bin/env python
"""Test script to debug Location admin template"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from church.admin import LocationAdmin
from django.template import engines

print("=" * 60)
print("LocationAdmin Configuration")
print("=" * 60)
print(f"change_form_template: {LocationAdmin.change_form_template}")
print(f"change_form_outer_before_template: {LocationAdmin.change_form_outer_before_template}")

# Check if templates exist
engine = engines['django']
print("\n" + "=" * 60)
print("Template Search")
print("=" * 60)

templates_to_check = [
    'admin/church/location_map.html',
    'admin/church/location_change_form.html',
    'admin/change_form.html',
]

for tpl in templates_to_check:
    try:
        template = engine.get_template(tpl)
        print(f"✅ {tpl} - FOUND")
        # Show first few lines
        content = template.template.source[:200]
        print(f"   Content preview: {content[:100]}...")
    except Exception as e:
        print(f"❌ {tpl} - NOT FOUND: {e}")

# Check Media
print("\n" + "=" * 60)
print("Media Files")
print("=" * 60)
media = LocationAdmin.Media()
print(f"CSS: {media._css}")
print(f"JS: {media._js}")
