"""
Script pour créer des données de test pour l'application Church
Exécutez avec: python manage.py shell < church/scripts/create_sample_data.py
"""

from django.contrib.auth.models import User
from church.models import Location, Church, UserProfile, GrowthConfig

# 1. Créer la configuration
config, created = GrowthConfig.objects.get_or_create(
    id=1,
    defaults={
        'label': 'Configuration Nationale',
        'required_points': 12,
        'period_days': 180,
        'absence_alert_days': 30
    }
)
print(f"✓ Configuration: {config.label}")

# 2. Créer les locations (Départements du Congo avec coordonnées)
locations_data = [
    {'name': 'Brazzaville', 'lat': -4.2634, 'lng': 15.2429},
    {'name': 'Pointe-Noire', 'lat': -4.7692, 'lng': 11.8636},
    {'name': 'Dolisie', 'lat': -4.1989, 'lng': 12.6664},
    {'name': 'Nkayi', 'lat': -4.1833, 'lng': 13.2833},
    {'name': 'Impfondo', 'lat': 1.6167, 'lng': 18.0667},
    {'name': 'Ouesso', 'lat': 1.6167, 'lng': 16.0500},
    {'name': 'Owando', 'lat': -0.4833, 'lng': 15.9000},
    {'name': 'Djambala', 'lat': -2.5500, 'lng': 14.7500},
    {'name': 'Kinkala', 'lat': -4.3667, 'lng': 14.7500},
    {'name': 'Ewo', 'lat': 0.8833, 'lng': 14.8333},
    {'name': 'Sibiti', 'lat': -3.6833, 'lng': 13.3500},
]

locations = {}
for loc_data in locations_data:
    location, created = Location.objects.get_or_create(
        name=loc_data['name'],
        defaults={
            'latitude': loc_data['lat'],
            'longitude': loc_data['lng']
        }
    )
    locations[loc_data['name']] = location
    if created:
        print(f"✓ Location créée: {location.name}")

# 3. Créer des églises
churches_data = [
    {'name': 'Église Centrale de Brazzaville', 'location': 'Brazzaville'},
    {'name': 'Église de Pointe-Noire Centre', 'location': 'Pointe-Noire'},
    {'name': 'Église de Dolisie', 'location': 'Dolisie'},
    {'name': 'Église de Nkayi', 'location': 'Nkayi'},
    {'name': 'Église de Owando', 'location': 'Owando'},
]

churches = {}
for church_data in churches_data:
    location = locations.get(church_data['location'])
    if location:
        church, created = Church.objects.get_or_create(
            name=church_data['name'],
            defaults={'location': location}
        )
        churches[church_data['name']] = church
        if created:
            print(f"✓ Église créée: {church.name} ({church.location.name})")

# 4. Créer des utilisateurs de test
users_data = [
    {
        'username': 'admin',
        'email': 'admin@church.cg',
        'password': 'admin123',
        'church': 'Église Centrale de Brazzaville',
        'role': 'ADMIN_CHURCH',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'username': 'agent_brazza',
        'email': 'agent@brazza.cg',
        'password': 'agent123',
        'church': 'Église Centrale de Brazzaville',
        'role': 'AGENT',
        'is_staff': False,
        'is_superuser': False
    },
    {
        'username': 'agent_pointe',
        'email': 'agent@pointe.cg',
        'password': 'agent123',
        'church': 'Église de Pointe-Noire Centre',
        'role': 'AGENT',
        'is_staff': False,
        'is_superuser': False
    },
    {
        'username': 'agent_dolisie',
        'email': 'agent@dolisie.cg',
        'password': 'agent123',
        'church': 'Église de Dolisie',
        'role': 'AGENT',
        'is_staff': False,
        'is_superuser': False
    },
]

for user_data in users_data:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'is_staff': user_data.get('is_staff', False),
            'is_superuser': user_data.get('is_superuser', False)
        }
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        
        church = churches.get(user_data['church'])
        if church:
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'church': church,
                    'role': user_data['role'],
                    'is_profile_complete': True
                }
            )
            print(f"✓ Utilisateur créé: {user.username} ({user_data['church']}) - MDP: {user_data['password']}")
        else:
            print(f"⚠ Église non trouvée pour {user.username}")
    else:
        print(f"• Utilisateur existe déjà: {user.username}")

print("\n" + "="*50)
print("DONNÉES DE TEST CRÉÉES AVEC SUCCÈS !")
print("="*50)
print("\n📋 Identifiants de connexion:")
print("   Admin: admin / admin123")
print("   Agent Brazzaville: agent_brazza / agent123")
print("   Agent Pointe-Noire: agent_pointe / agent123")
print("   Agent Dolisie: agent_dolisie / agent123")
print("\n⚠️  Chaque utilisateur doit sélectionner sa ville")
print("   correspondant à son église lors de la connexion.")
print("="*50)
