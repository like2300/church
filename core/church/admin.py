from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import (
    GrowthConfig, Location, Church, UserProfile,
    Member, CulteType, CulteSession, Attendance, AbsenceAlert, Card
)

# Custom Admin Site Configuration
admin.site.site_header = "Church Administration"
admin.site.site_title = "Church Dashboard"
admin.site.index_title = "Dashboard"


@admin.register(GrowthConfig)
class GrowthConfigAdmin(ModelAdmin):
    list_display = ('label', 'required_attendances', 'promotion_days', 'absence_limit_days')
    readonly_fields = ('id',)
    fieldsets = (
        ("Configuration de Croissance", {
            "description": "Définissez les seuils pour la transformation Visiteur → Membre Actif",
            "fields": ("label", "required_attendances", "promotion_days", "absence_limit_days"),
        }),
    )


@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)
    save_on_top = True
    
    fieldsets = (
        ("Informations Géographiques", {
            "fields": ("name", "latitude", "longitude"),
        }),
        ("📍 Carte Interactive", {
            "fields": ("interactive_map",),
            "description": "Cliquez sur la carte pour définir les coordonnées automatiquement",
        }),
    )
    
    readonly_fields = ('interactive_map',)
    
    def interactive_map(self, obj=None):
        from django.utils.safestring import mark_safe
        return mark_safe('''
            <div style="margin: 20px 0;">
                <div id="location-map" style="height: 400px; width: 100%; border-radius: 8px; background: #f0f4f8; border: 2px solid #e5e7eb;"></div>
                <div id="map-error" style="display:none; margin-top: 10px; padding: 10px; background: #fee; border: 1px solid #fcc; border-radius: 4px; color: #c00;">⚠️ Erreur de chargement</div>
                <div style="margin-top: 16px; padding: 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;">
                    <strong style="color: #1d4ed8;">📌 Instructions:</strong>
                    <ul style="color: #1e40af; margin: 8px 0 0 20px; font-size: 13px;">
                        <li>Cliquez sur la carte pour définir les coordonnées GPS</li>
                        <li>Survolez un département pour voir son nom</li>
                        <li>Les champs Latitude/Longitude sont remplis automatiquement</li>
                    </ul>
                </div>
            </div>
            <style>
            #location-map { z-index: 1 !important; position: relative; }
            .leaflet-container { z-index: 1 !important; font-family: inherit !important; }
            .leaflet-pane { z-index: 10 !important; }
            .leaflet-popup-content-wrapper { z-index: 100 !important; border-radius: 8px !important; }
            </style>
            <script>
            (function() {
                if (typeof L === 'undefined') { document.getElementById('map-error').style.display = 'block'; return; }
                setTimeout(function() {
                    var map = L.map('location-map').setView([-1.5, 15.0], 6);
                    fetch('/static/data/congo_departments.geojson')
                        .then(function(r) { if (!r.ok) throw new Error(r.status); return r.json(); })
                        .then(function(data) {
                            var layer = L.geoJSON(data, {
                                style: function() { return { color: '#2563eb', weight: 2, fillOpacity: 0.2 }; },
                                onEachFeature: function(f, l) {
                                    if (f.properties && f.properties.name) l.bindPopup('<b>' + f.properties.name + '</b><br>Chef-lieu: ' + f.properties.chef_lieu);
                                }
                            }).addTo(map);
                            map.fitBounds(layer.getBounds());
                            setTimeout(function() { map.invalidateSize(); }, 100);
                        })
                        .catch(function(e) { document.getElementById('map-error').style.display = 'block'; });
                    map.on('click', function(e) {
                        var lat = document.getElementById('id_latitude');
                        var lng = document.getElementById('id_longitude');
                        if (lat) lat.value = e.latlng.lat.toFixed(4);
                        if (lng) lng.value = e.latlng.lng.toFixed(4);
                    });
                }, 500);
            })();
            </script>
        ''')
    
    interactive_map.short_description = "Carte Interactive"
    
    class Media:
        css = {'all': ('leaflet/leaflet.css',)}
        js = ('leaflet/leaflet.js',)


@admin.register(Church)
class ChurchAdmin(ModelAdmin):
    list_display = ('name', 'location')
    list_filter = ('location',)
    search_fields = ('name',)
    fieldsets = (
        ("Informations de l'Église", {
            "fields": ("name", "location"),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'church', 'role', 'is_profile_complete')
    list_filter = ('role', 'church')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    fieldsets = (
        ("Profil Utilisateur", {
            "fields": ("user", "church", "role", "is_profile_complete"),
        }),
    )


@admin.register(Member)
class MemberAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'genre', 'church', 'status', 'date_joined')
    list_filter = ('status', 'genre', 'church')
    search_fields = ('first_name', 'last_name', 'phone')
    list_per_page = 20
    date_hierarchy = 'date_joined'
    readonly_fields = ('date_joined',)
    fieldsets = (
        ("Informations Personnelles", {
            "fields": ("first_name", "last_name", "genre", "phone"),
        }),
        ("Informations Église", {
            "fields": ("church", "status"),
        }),
        ("Dates", {
            "fields": ("date_joined",),
            "classes": ("collapse",),
        }),
    )


@admin.register(CulteType)
class CulteTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CulteSession)
class CulteSessionAdmin(ModelAdmin):
    list_display = ('theme', 'church', 'culte_type', 'date', 'officiant')
    list_filter = ('church', 'culte_type', 'date')
    search_fields = ('theme', 'officiant')
    date_hierarchy = 'date'
    list_per_page = 20
    raw_id_fields = ('church', 'culte_type')
    fieldsets = (
        ("Informations de la Session", {
            "fields": ("church", "culte_type", "theme", "date", "officiant"),
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ('member', 'culte_session', 'recorded_at')
    list_filter = ('culte_session__date', 'member__church')
    search_fields = ('member__first_name', 'member__last_name')
    date_hierarchy = 'recorded_at'
    list_per_page = 20
    raw_id_fields = ('member', 'culte_session')
    fieldsets = (
        ("Enregistrement de Présence", {
            "fields": ("culte_session", "member"),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Allow superusers to bypass church validation
        if request.user.is_superuser:
            obj.save(skip_validation=True)
        else:
            obj.save()


@admin.register(AbsenceAlert)
class AbsenceAlertAdmin(ModelAdmin):
    list_display = ('member', 'church', 'last_seen', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'church')
    search_fields = ('member__first_name', 'member__last_name')
    fieldsets = (
        ("Alerte d'Absence", {
            "fields": ("church", "member", "last_seen", "is_resolved", "pastoral_notes"),
        }),
    )


@admin.register(Card)
class CardAdmin(ModelAdmin):
    list_display = ('card_number', 'member', 'issue_date', 'expiry_date', 'status', 'created_at')
    list_filter = ('status', 'member__church')
    search_fields = ('card_number', 'member__first_name', 'member__last_name')
    date_hierarchy = 'created_at'
    list_per_page = 20
    readonly_fields = ('card_number', 'created_at')
    fieldsets = (
        ("Informations de la Carte", {
            "fields": ("card_number", "member", "status"),
        }),
        ("Dates", {
            "fields": ("issue_date", "expiry_date", "created_at"),
        }),
    )
