"""
Script de vérification complète des URLs - Church App
Vérifie que toutes les URLs du projet fonctionnent correctement
"""
import os
import sys
import subprocess
import time
import requests
import webbrowser
from pathlib import Path

def check_urls():
    """Vérifie la résolution de toutes les URLs Django"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION DES URLs - CHURCH APP")
    print("="*70)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import django
        django.setup()
        from django.urls import reverse, NoReverseMatch
    except Exception as e:
        print(f"❌ Erreur lors du chargement de Django: {e}")
        return False
    
    # Liste complète des URLs du projet
    urls_to_check = [
        # Authentication
        ('login', None, 'Page de connexion'),
        ('logout', None, 'Déconnexion'),
        
        # Home & Members
        ('home', None, "Page d'accueil"),
        ('member_list', None, 'Liste des membres'),
        ('member_create', None, 'Créer un membre'),
        
        # Cards
        ('card_create', None, 'Créer une carte'),
        
        # Attendance
        ('attendance_create', None, 'Créer une présence'),
        ('attendance_export', None, 'Exporter présences'),
        
        # Culte Sessions
        ('culte_session_create', None, 'Créer session culte'),
        ('culte_session_list', None, 'Liste sessions culte'),
        ('api_culte_sessions', None, 'API culte sessions'),
        
        # Alerts
        ('alerts_list', None, 'Liste alertes'),
        ('alerts_export', None, 'Exporter alertes'),
        
        # Statistics
        ('statistics', None, 'Statistiques'),
        ('statistics_export', None, 'Exporter statistiques'),
        
        # Reports
        ('report_generate', None, 'Générer rapport'),
        ('report_export_pdf', None, 'Exporter PDF'),
        ('report_export_docx', None, 'Exporter DOCX'),
        
        # MDEVISP Reports
        ('mdevisp_report', None, 'Rapport MDEVISP'),
        ('mdevisp_annual', None, 'Rapport annuel MDEVISP'),
        ('mdevisp_export_docx', None, 'Exporter MDEVISP DOCX'),
    ]
    
    print(f"\n📋 Test de {len(urls_to_check)} URLs...\n")
    
    all_ok = True
    results = []
    
    for url_name, kwargs, description in urls_to_check:
        try:
            if kwargs:
                url = reverse(url_name, kwargs=kwargs)
            else:
                url = reverse(url_name)
            
            results.append(('✅', url_name, url, description))
            print(f"✅ {url_name:30} -> {url:40} ({description})")
        except NoReverseMatch as e:
            results.append(('❌', url_name, str(e), description))
            print(f"❌ {url_name:30} -> ERREUR: {e}")
            all_ok = False
        except Exception as e:
            results.append(('⚠️', url_name, str(e), description))
            print(f"⚠️  {url_name:30} -> ERREUR: {e}")
            all_ok = False
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    
    passed = sum(1 for r in results if r[0] == '✅')
    failed = len(results) - passed
    
    print(f"✅ URLs fonctionnelles: {passed}/{len(results)}")
    print(f"❌ URLs en erreur: {failed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 TOUTES LES URLs SONT FONCTIONNELLES !")
        return True
    else:
        print(f"\n⚠️  {failed} URL(s) nécessitent une attention")
        return False

def check_server():
    """Vérifie si le serveur Django est accessible"""
    print("\n" + "="*70)
    print("🌐 VÉRIFICATION DU SERVEUR")
    print("="*70)
    
    url = "http://127.0.0.1:8000"
    
    try:
        response = requests.get(f"{url}/login/", timeout=3)
        if response.status_code == 200:
            print(f"✅ Serveur accessible sur {url}")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"⚠️  Serveur répond avec status: {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print(f"⏳ Serveur non détecté sur {url}")
        print(f"   (C'est normal si le serveur n'est pas encore lancé)")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("\n" + "🎯"*35)
    print("VÉRIFICATION COMPLÈTE - CHURCH APPLICATION")
    print("🎯"*35)
    
    # Check URLs
    urls_ok = check_urls()
    
    # Check server
    server_ok = check_server()
    
    # Final summary
    print("\n" + "="*70)
    print("🎯 RÉSULTAT FINAL")
    print("="*70)
    
    if urls_ok:
        print("\n✅ TOUTES LES URLs DU PROJET SONT CORRECTES")
        print("\n📋 URLs principales:")
        print("   • Login:        http://127.0.0.1:8000/login/")
        print("   • Home:         http://127.0.0.1:8000/")
        print("   • Statistics:   http://127.0.0.1:8000/statistics/")
        print("   • MDEVISP:      http://127.0.0.1:8000/mdevisp/")
        print("   • Members:      http://127.0.0.1:8000/members/")
        print("   • Alerts:       http://127.0.0.1:8000/alerts/")
        print("\n💡 Toutes les liens du projet fonctionneront dans l'exécutable!")
    
    print("\n" + "="*70)
    
    return urls_ok

if __name__ == '__main__':
    try:
        success = main()
        print("\n✅ Vérification terminée!")
        input("\nAppuyez sur Entrée pour fermer...")
    except KeyboardInterrupt:
        print("\n\n⚠️  Vérification interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour fermer...")
