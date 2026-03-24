from django import forms
from .models import Member, Attendance, CulteSession, Card
import re


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'genre', 'phone', 'status']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0',
                'placeholder': 'Prénom du membre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0',
                'placeholder': 'Nom du membre'
            }),
            'genre': forms.Select(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0',
                'placeholder': '+242 XX XXX XX XX',
                'title': 'Le numéro doit commencer par +242 (Congo) ou un autre indicatif pays'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0'
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        
        # Si le champ est vide, on le permet (champ optionnel dans le modèle)
        if not phone:
            return phone
        
        # Vérifier que le numéro commence par un '+' suivi de l'indicatif pays
        if not phone.startswith('+'):
            raise forms.ValidationError(
                'Le numéro de téléphone doit commencer par un indicatif pays (ex: +242 pour le Congo, +33 pour la France, etc.)'
            )
        
        # Vérifier qu'il y a des chiffres après l'indicatif
        phone_without_plus = phone[1:]  # Enlever le '+'
        if not phone_without_plus.isdigit() or len(phone_without_plus) < 8:
            raise forms.ValidationError(
                'Le numéro de téléphone doit contenir au moins 8 chiffres après l\'indicatif pays'
            )
        
        # Format recommandé pour le Congo
        if phone.startswith('+242') and len(phone_without_plus) != 12:
            raise forms.ValidationError(
                'Pour le Congo (+242), le numéro doit contenir 12 chiffres au total (ex: +242 06 123 45 67)'
            )
        
        return phone


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['member', 'culte_session']
        widgets = {
            'member': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'culte_session': forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }


class CulteSessionForm(forms.ModelForm):
    class Meta:
        model = CulteSession
        fields = ['culte_type', 'theme', 'date', 'officiant']
        widgets = {
            'culte_type': forms.Select(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0'
            }),
            'theme': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0',
                'placeholder': 'Thème du culte'
            }),
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0'
            }),
            'officiant': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-200 p-3 text-sm focus:border-blue-500 focus:ring-0',
                'placeholder': 'Nom du prédicateur'
            }),
        }


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['member', 'issue_date', 'expiry_date', 'status']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'issue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
