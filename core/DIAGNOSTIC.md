# Diagnostic: Problèmes de l'Exécutable Church App

## ✅ BONNE NOUVELLE: Vos liens sont CORRECTS!

Les liens dans `statistics.html` sont bien configurés:

```html
<a href="{% url 'mdevisp_report'%}">
```

Ce lien est **CORRECT** et correspond à l'URL définie dans `church/urls.py`:
```python
path('mdevisp/', views.mdevisp_report, name='mdevisp_report'),
```

## 🔍 PROBLÈME IDENTIFIÉ: Le navigateur ne s'ouvre pas automatiquement

### Causes possibles:

1. **Le serveur Django met du temps à démarrer** dans l'exécutable
2. **Le port 8000 est déjà utilisé** par un autre processus
3. **L'ouverture du navigateur est bloquée** par la sécurité Windows

### ✅ SOLUTION: Modifications appliquées au launcher

J'ai amélioré `launcher.py` avec:

1. **Délai plus long** avant l'ouverture du navigateur (1 seconde au lieu de 500ms)
2. **Double méthode** pour ouvrir le navigateur (subprocess + webbrowser)
3. **Meilleur affichage** des erreurs si le navigateur ne s'ouvre pas

## 📋 INSTRUCTIONS POUR TESTER

### Option 1: Reconstruire l'exécutable (RECOMMANDÉ)

```bash
# Dans le terminal
cd c:\Bureau\church\core
pyinstaller ChurchApp.spec
```

Puis lancez l'exécutable créé dans `dist\ChurchApp.exe`

### Option 2: Tester sans reconstruire

1. Lancez `launcher.py` directement:
```bash
python launcher.py
```

2. Regardez les logs dans la fenêtre Tkinter
3. Si vous voyez "✅ Serveur sur port 8000", le serveur fonctionne
4. Cliquez sur "🌐 Ouvrir le navigateur"

### Option 3: Ouvrir manuellement

Si le serveur est lancé mais le navigateur ne s'ouvre pas:
- Ouvrez votre navigateur manuellement
- Allez à: **http://127.0.0.1:8000**
- Vos liens fonctionneront!

## 🔧 VÉRIFICATIONS

### Vérifier que les URLs fonctionnent:

```bash
python manage.py shell
```

Puis dans le shell:
```python
from django.urls import reverse
reverse('mdevisp_report')  # Doit retourner: '/mdevisp/'
reverse('statistics_export')  # Doit retourner: '/statistics/export/'
```

### Vérifier le port 8000:

```bash
netstat -ano | findstr :8000
```

Si le port est utilisé, tuez le processus:
```bash
taskkill /PID <PID> /F
```

## 📊 STRUCTURE DES URLs

```
http://127.0.0.1:8000/
├── statistics/              ← Page actuelle
├── mdevisp/                 ← Centre de Rapports (votre lien)
├── statistics/export/       ← Export Excel
└── ... autres URLs
```

## ✅ CONCLUSION

Vos liens dans `statistics.html` sont **CORRECTS**. Le problème vient du launcher qui:
- Soit ne démarre pas complètement
- Soit met trop de temps à ouvrir le navigateur
- Soit a un problème de permissions

La modification apportée à `launcher.py` devrait résoudre ces problèmes après reconstruction de l'exécutable.
