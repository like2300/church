# 📊 EXPORT EXCEL PROFESSIONNEL - Statistiques

## ✅ Fonctionnalité implémentée

L'export Excel depuis la page `/statistics/` génère maintenant un **vrai fichier .xlsx** avec :

### 📁 Structure du fichier Excel

```
Statistiques_PAROISSE_2026-02-24_to_2026-03-26.xlsx
├── Feuille: "Statistiques"
│   ├── Ligne 1:    En-tête avec titre (fusionné A1:D1)
│   ├── Ligne 2:    Période du rapport
│   ├── Section 1:  STATISTIQUES MEMBRES (lignes 4-11)
│   ├── Section 2:  CULTES & PRÉSENCES (lignes 12-18)
│   ├── Section 3:  DÉTAIL PAR TYPE DE CULTE (lignes 19-34)
│   ├── Section 4:  FORMULES DE CALCUL (lignes 35-44)
│   └── Pied:       Génération du rapport (ligne 45)
```

---

## 📊 Sections du rapport Excel

### 1. **STATISTIQUES MEMBRES** (Lignes 5-11)

| Colonne A | Colonne B | Colonne C | Colonne D |
|-----------|-----------|-----------|-----------|
| **Indicateur** | **Effectif** | **Pourcentage** | **Formule** |
| Total Membres | 150 | 100% | `=B6/SUM($B$6:$B$10)*100` |
| Membres Actifs | 120 | 80.0% | `=B7/SUM($B$6:$B$10)*100` |
| Visiteurs | 30 | 20.0% | `=B8/SUM($B$6:$B$10)*100` |
| Hommes | 70 | 46.7% | `=B9/$B$6*100` |
| Femmes | 60 | 40.0% | `=B10/$B$6*100` |
| Enfants | 20 | 13.3% | `=B11/$B$6*100` |

**Caractéristiques :**
- ✅ Cellules avec bordures fines
- ✅ En-têtes en bleu clair (#93C5FD)
- ✅ Première colonne avec fond alterné
- ✅ Pourcentages calculés automatiquement
- ✅ Formules Excel réelles dans la colonne D

---

### 2. **CULTES & PRÉSENCES** (Lignes 13-18)

| Colonne A | Colonne B | Colonne C | Colonne D |
|-----------|-----------|-----------|-----------|
| **Indicateur** | **Valeur** | **Formule Excel** | **Note** |
| Total Cultes | 12 | `=COUNTA(A14:A100)` | |
| Total Présences | 360 | `=SUM(B14:B100)` | |
| Membres Actifs | 120 | `=B7` | Référence section 1 |
| Taux de Participation | 250.0% | `=B15/(B16*B14)*100` | **Formule MDEVISP** |

**Caractéristiques :**
- ✅ Taux de participation en surbrillance jaune (#FEF3C7)
- ✅ Formule MDEVISP officielle
- ✅ Références croisées entre sections

---

### 3. **DÉTAIL PAR TYPE DE CULTE** (Lignes 20-34)

| Colonne A | Colonne B | Colonne C | Colonne D |
|-----------|-----------|-----------|-----------|
| **Type de Culte** | **Présences** | **Pourcentage** | **Barre** |
| Culte Dominical | 200 | 55.6% | `=B21/SUM($B$21:$B$31)*100` |
| Étude Biblique | 100 | 27.8% | `=B22/SUM($B$21:$B$31)*100` |
| Réveil | 60 | 16.7% | `=B23/SUM($B$21:$B$31)*100` |

**Caractéristiques :**
- ✅ Dynamique selon les types de cultes existants
- ✅ Pourcentages calculés automatiquement
- ✅ Formules de référence relative

---

### 4. **FORMULES DE CALCUL** (Lignes 36-39)

| Colonne A | Colonne B |
|-----------|-----------|
| **Nom** | **Description** |
| Taux de Participation | `=(Total Présences / (Membres Actifs × Nb Cultes)) × 100` |
| Pourcentage par Genre | `=(Effectif Genre / Total Membres) × 100` |
| Pourcentage par Type | `=(Présences Type / Total Présences) × 100` |
| Seuil d'alerte | `< 40% = Participation insuffisante` |

---

## 🎨 Mise en forme appliquée

### Polices
```python
- Titre: Calibri 16pt, Blanc, Gras
- En-têtes: Calibri 12pt, Blanc, Gras
- Normal: Calibri 11pt
- Pied: Calibri 9pt, Gris, Italique
```

### Couleurs
```python
- Titre: Fond Bleu Foncé (#1E40AF)
- En-têtes section: Fond Bleu (#3B82F6)
- En-têtes tableau: Fond Bleu Clair (#93C5FD)
- Lignes paires: Fond Bleu Très Clair (#EFF6FF)
- Surbrillance: Fond Jaune (#FEF3C7)
```

### Bordures
```python
- Toutes les cellules: Bordures fines noires
- Alignement: Centré pour chiffres, Gauche pour texte
```

---

## 📊 Formules Excel utilisées

### Formules de pourcentage :
```excel
=B6/SUM($B$6:$B$10)*100     ← Pourcentage du total
=B9/$B$6*100                 ← Pourcentage par genre
```

### Formules de référence :
```excel
=B7                          ← Référence cellule existante
=COUNTA(A14:A100)            ← Compter cellules non vides
=SUM(B14:B100)               ← Somme plage
```

### Formule MDEVISP :
```excel
=B15/(B16*B14)*100           ← Taux de participation
```

---

## 🔧 Comment utiliser

### 1. **Depuis la page Statistics**
```
1. Allez sur: http://127.0.0.1:8000/statistics/
2. (Optionnel) Sélectionnez une période
3. Cliquez sur "Exporter Excel"
4. Téléchargez le fichier .xlsx
```

### 2. **Dans Excel**
```
1. Ouvrez le fichier téléchargé
2. Les données sont déjà formatées
3. Les formules Excel sont actives
4. Vous pouvez modifier les valeurs et les formules se mettront à jour
```

### 3. **Personnalisation**
```
- Modifiez les cellules pour tester des scénarios
- Les pourcentages se recalculent automatiquement
- Ajoutez des graphiques avec les données
```

---

## ✅ Avantages de cet export

| Caractéristique | Description |
|-----------------|-------------|
| **Vrai format .xlsx** | Compatible Excel 2007+ |
| **Formules actives** | Recalcul automatique |
| **Mise en forme pro** | Couleurs, bordures, alignement |
| **Données réelles** | 100% depuis la base de données |
| **Références croisées** | Cellules liées entre sections |
| **Documentation incluse** | Section 4 explique les formules |

---

## 📝 Exemple d'utilisation

**Scénario :** Vous voulez projeter une augmentation de 10% des présences

1. Ouvrez le fichier Excel exporté
2. Allez à la cellule B15 (Total Présences)
3. Multipliez par 1.1 : `=B15*1.1`
4. Le taux de participation (B17) se met à jour automatiquement !

---

## 🚀 Technologies utilisées

```python
- openpyxl: Bibliothèque Excel professionnelle
- Django: Framework web
- BytesIO: Buffer mémoire pour génération rapide
```

**Fichier généré :** `Statistiques_Paroisse_2026-02-24_to_2026-03-26.xlsx`

---

## ⚠️ Requirements

Pour que l'export Excel fonctionne, installez openpyxl :

```bash
pip install openpyxl
```

Si openpyxl n'est pas installé, un message d'erreur s'affichera.
