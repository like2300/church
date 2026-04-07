from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
import uuid

# ==========================================================
# 1. CONFIGURATION DYNAMIQUE (Le "Cerveau" de l'App)
# ==========================================================
class GrowthConfig(models.Model):
    """
    Permet à l'Admin National de régler les seuils sans coder.
    Exemple : 3 mois (90j) pour devenir actif, 1 mois (30j) pour l'alerte.
    """
    label = models.CharField(max_length=100, default="Configuration Standard")
    required_attendances = models.PositiveIntegerField(default=3, verbose_name="Présences requises")
    promotion_days = models.PositiveIntegerField(default=90, verbose_name="Période promotion (jours)")
    absence_limit_days = models.PositiveIntegerField(default=30, verbose_name="Seuil alerte absence (jours)")

    class Meta:
        verbose_name = "Paramètre de Croissance"
        verbose_name_plural = "⚙️ Paramètres de Croissance"

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(id=1)
        return config

    def __str__(self):
        return self.label


# ==========================================================
# 2. GÉOGRAPHIE DU CONGO (Pour le Zoom sur la Map au Login)
# ==========================================================
class Location(models.Model):
    """Villes et Districts du Congo avec coordonnées GPS pour l'effet de Zoom UI"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Ville/District")
    latitude = models.FloatField(null=True, blank=True, help_text="Coordonnée pour le zoom Map")
    longitude = models.FloatField(null=True, blank=True, help_text="Coordonnée pour le zoom Map")

    class Meta:
        verbose_name = "📍 Département"
        verbose_name_plural = "📍 Départements du Congo"
        ordering = ['name']

    def __str__(self):
        return self.name


class Church(models.Model):
    """Églises locales rattachées à une zone géographique"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'Église")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='churches')
    
    class Meta:
        verbose_name = "🏛️ Église Locale"
        verbose_name_plural = "🏛️ Églises Locales"
        ordering = ['location', 'name']

    def __str__(self):
        return f"{self.name} ({self.location.name})"


# ==========================================================
# 3. AUTHENTIFICATION ET PROFILS (Admin vs Agent)
# ==========================================================
class UserProfile(models.Model):
    """
    Profil complété après authentification. 
    Lie l'utilisateur à son Église locale et définit son rôle.
    """
    ROLES = [
        ('ADMIN_CHURCH', "Administrateur d'Église"), 
        ('AGENT', 'Agent de Saisie')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='AGENT')
    is_profile_complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "👤 Profil Utilisateur"
        verbose_name_plural = "👤 Profils Utilisateurs"

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.church.name})"


# ==========================================================
# 4. GESTION DES MEMBRES (Statistiques par Genre & Statut)
# ==========================================================
class Member(models.Model):
    """Fidèles (Visiteurs ou Actifs) avec distinction de Genre (H/F/E)"""
    GENRE_CHOICES = [
        ('H', 'Homme'), 
        ('F', 'Femme'), 
        ('E', 'Enfant')
    ]
    STATUS_CHOICES = [
        ('VISITOR', 'Visiteur'), 
        ('REGULAR', 'Membre Actif')
    ]
    
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES, verbose_name="Genre")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='members')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='VISITOR', verbose_name="Statut")
    date_joined = models.DateField(auto_now_add=True, verbose_name="Date d'adhésion")

    class Meta:
        verbose_name = "🙏 Membre/Fidèle"
        verbose_name_plural = "🙏 Membres/Fidèles"
        ordering = ['church', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['church', 'status']),
            models.Index(fields=['status', 'genre']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_genre_display()})"

    def update_growth_status(self):
        """
        LOGIQUE AUTOMATIQUE : 
        Vérifie si le visiteur a atteint le quota de présences en 3 mois.
        """
        config = GrowthConfig.get_config()
        date_limite = timezone.now() - timedelta(days=config.promotion_days)
        
        # Compte les présences réelles dans l'historique
        presence_count = Attendance.objects.filter(
            member=self, 
            culte_session__date__gte=date_limite
        ).count()

        if presence_count >= config.required_attendances and self.status == 'VISITOR':
            self.status = 'REGULAR'
            self.save()


# ==========================================================
# 5. HISTORIQUE DES CULTES (Rapports Automatiques)
# ==========================================================
class CulteType(models.Model):
    """Types : Culte Dominical, Étude Biblique, Réveil, etc."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Type de Culte")
    
    class Meta:
        verbose_name = "📖 Type de Culte"
        verbose_name_plural = "📖 Types de Cultes"
        ordering = ['name']

    def __str__(self):
        return self.name


class CulteSession(models.Model):
    """
    Une session de culte spécifique. 
    Sert de base pour le calcul du rapport automatique (H/F/E).
    """
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='cultes', verbose_name="Église")
    culte_type = models.ForeignKey(CulteType, on_delete=models.CASCADE, verbose_name="Type de culte")
    theme = models.CharField(max_length=255, verbose_name="Thème du message")
    date = models.DateTimeField(verbose_name="Date et Heure")
    officiant = models.CharField(max_length=200, blank=True, null=True, verbose_name="Officiant/Prédicateur")

    class Meta:
        verbose_name = "✝️ Session de Culte"
        verbose_name_plural = "✝️ Sessions de Culte"
        # Empêche les doublons même en mode hors-ligne
        unique_together = ('church', 'culte_type', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['church', '-date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.theme} - {self.date.strftime('%A %d %B %Y')}"

    def get_attendance_stats(self):
        """
        CALCUL DYNAMIQUE : Mâche le travail de la View pour le rapport.
        Retourne les totaux par genre pour cette session.
        """
        return self.attendances.aggregate(
            total=Count('id'),
            hommes=Count('id', filter=Q(member__genre='H')),
            femmes=Count('id', filter=Q(member__genre='F')),
            enfants=Count('id', filter=Q(member__genre='E'))
        )


# ==========================================================
# 6. POINTAGES (L'Historique des Présences)
# ==========================================================
class Attendance(models.Model):
    """Lien entre un Membre et une Session de Culte - Registre de présence"""
    culte_session = models.ForeignKey(CulteSession, on_delete=models.CASCADE, related_name='attendances', verbose_name="Session de culte")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='history', verbose_name="Membre")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Enregistré le")

    class Meta:
        verbose_name = "✅ Pointage/Présence"
        verbose_name_plural = "✅ Pointages/Présences"
        unique_together = ('culte_session', 'member')
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['culte_session', '-recorded_at']),
            models.Index(fields=['member', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.member} - {self.culte_session.date.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # Un membre peut être présent dans plusieurs églises différentes (visiteurs, déplacements)
        # La validation est donc supprimée pour permettre cette flexibilité
        
        super().save(*args, **kwargs)
        
        # Déclenche la vérification du statut (Visiteur -> Actif)
        # Seulement pour les membres de l'église où a lieu le culte
        if self.member.church == self.culte_session.church:
            self.member.update_growth_status()


# ==========================================================
# 7. ALERTES D'ABSENCE (Suivi Pastoral)
# ==========================================================
class AbsenceAlert(models.Model):
    """Alertes pour les membres actifs absents depuis 1 mois (30j)"""
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='alerts', verbose_name="Église")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Membre absent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Dernière présence")
    is_resolved = models.BooleanField(default=False, verbose_name="Visite/Appel effectué")
    pastoral_notes = models.TextField(blank=True, verbose_name="Notes du suivi pastoral")

    class Meta:
        verbose_name = "⚠️ Alerte d'Absence"
        verbose_name_plural = "⚠️ Alertes d'Absences"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['church', 'is_resolved']),
            models.Index(fields=['is_resolved', '-created_at']),
        ]

    def __str__(self):
        status = "✅ Résolu" if self.is_resolved else "⏳ En attente"
        return f"{status} - {self.member.last_name} ({self.church.name})"


# ==========================================================
# 8. CARTES DE MEMBRE (Carte d'identification)
# ==========================================================
class Card(models.Model):
    """Carte d'identification pour les membres avec code QR unique"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expirée'),
        ('LOST', 'Perdue'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='cards', verbose_name="Membre")
    card_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de carte")
    issue_date = models.DateField(default=date.today, verbose_name="Date d'émission")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Date d'expiration")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "🪪 Carte de Membre"
        verbose_name_plural = "🪪 Cartes de Membre"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member', 'status']),
            models.Index(fields=['card_number']),
        ]

    def __str__(self):
        return f"Carte {self.card_number} - {self.member.first_name} {self.member.last_name}"

    def save(self, *args, **kwargs):
        if not self.card_number:
            # Generate unique card number: CHURCH-YYYY-UUID(8)
            church_prefix = self.member.church.name[:3].upper().replace(' ', '')
            year = timezone.now().year
            unique_id = str(uuid.uuid4())[:8].upper()
            self.card_number = f"{church_prefix}-{year}-{unique_id}"
        super().save(*args, **kwargs)
