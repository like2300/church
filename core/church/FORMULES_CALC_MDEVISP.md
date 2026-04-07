# 📊 FORMULES DE CALCUL - Système MDEVISP

## Formules Officielles (Cahier des Charges)

### 1. Totaux de base
```
N = Nombre de cultes matinaux
M = Nombre de cultes vespéraux
T = Nombre de cultes dominicaux

X = N + M + T  (Total général des cultes)
```

### 2. Pourcentage de participation
```
Y = Effectif total (membres actifs REGULAR)

Formule CDC : % = (X / Y) × 100

INTERPRÉTATION PRATIQUE IMPLÉMENTÉE :
% = (Total Présences / (Effectif × Nombre de cultes)) × 100
```

**Pourquoi cette interprétation ?**
- La formule brute `(X / Y) × 100` donnerait : `(Nb cultes / Membres) × 100`
- Ce qui n'a pas de sens car on compare des cultes à des personnes
- L'interprétation correcte est : `(Présences / (Membres × Cultes)) × 100`
- Cela donne le **taux de participation moyen par culte**

### 3. Exemple concret
```
Données :
- 10 membres actifs (Y)
- 4 cultes dans le mois (X = N+M+T = 4)
- 120 présences totales enregistrées

Calcul :
% = (120 / (10 × 4)) × 100
% = (120 / 40) × 100
% = 3 × 100
% = 300%
```

**Interprétation :**
- 100% = Tous les membres viennent à tous les cultes
- 300% = Chaque membre vient en moyenne à 3 cultes
- < 100% = Certains membres manquent des cultes

### 4. Seuil d'alerte
```
Seuil minimal : 40%
Alerte déclenchée si : Pourcentage < 40%
```

---

## Implémentation dans le code

### Fichier : `church/views.py`

#### 1. Vue `statistics` (ligne ~747)
```python
# Taux de participation
if regular_members > 0 and total_cultes > 0:
    participation_rate = round((total_presences / (regular_members * total_cultes)) * 100, 1)
else:
    participation_rate = 0
```

**Formule :** `(Présences / (Membres × Cultes)) × 100`

#### 2. Vue `mdevisp_report` (ligne ~1345)
```python
# Pourcentage mensuel MDEVISP
if effectif_total > 0 and total_cultes_actuel > 0:
    pourcentage_mensuel = round((presences_actuel / (effectif_total * total_cultes_actuel)) * 100, 1)
else:
    pourcentage_mensuel = 0
```

**Formule :** `(Présences / (Effectif × Cultes)) × 100`

#### 3. Pourcentages par type de culte (ligne ~703)
```python
for ct in culte_types:
    count = attendances_qs.filter(culte_session__culte_type=ct).count()
    percentage = round((count / total_presences * 100) if total_presences > 0 else 0, 1)
```

**Formule :** `(Présences du type / Total présences) × 100`

---

## Récapitulatif des formules

| Indicateur | Formule | Fichier | Ligne |
|------------|---------|---------|-------|
| **Total membres** | `COUNT(Member WHERE church=X)` | views.py | ~686 |
| **Membres actifs** | `COUNT(Member WHERE status='REGULAR')` | views.py | ~688 |
| **Total cultes** | `COUNT(CulteSession WHERE date IN periode)` | views.py | ~689 |
| **Total présences** | `COUNT(Attendance WHERE culte_session IN periode)` | views.py | ~690 |
| **Pourcentage par type** | `(Présences type / Total présences) × 100` | views.py | ~705 |
| **Taux participation** | `(Présences / (Membres × Cultes)) × 100` | views.py | ~749 |
| **Pourcentage MDEVISP** | `(Présences / (Effectif × Cultes)) × 100` | views.py | ~1345 |

---

## Vérification de la conformité

### ✅ Ce qui est CORRECT :

1. **Calcul des totaux N, M, T** : ✅ Correct
   - `cultes_matinaux = sessions.filter(culte_type=culte_matinal).count()`
   - `cultes_vesperaux = sessions.filter(culte_type=culte_vesperal).count()`
   - `cultes_dominicaux = sessions.filter(culte_type=culte_dominical).count()`

2. **Calcul de X = N + M + T** : ✅ Correct
   - `total_cultes = cultes_matinaux + cultes_vesperaux + cultes_dominicaux`

3. **Calcul de Y (effectif)** : ✅ Correct
   - `effectif_total = Member.objects.filter(status='REGULAR').count()`

4. **Calcul du pourcentage** : ✅ Correct (interprétation pratique)
   - `(presences / (effectif * cultes)) * 100`

5. **Seuil d'alerte à 40%** : ✅ Correct
   - `alerte_seuil = pourcentage_mensuel < 40`

### ⚠️ Points d'attention :

1. **La formule brute du CDC** `(X / Y) × 100` n'a pas de sens mathématique
   - X = nombre de cultes (ex: 4)
   - Y = nombre de membres (ex: 10)
   - (4 / 10) × 100 = 40% → Ce n'est pas un taux de participation !

2. **L'interprétation correcte** est celle implémentée :
   - `(Présences / (Membres × Cultes)) × 100`
   - (120 / (10 × 4)) × 100 = 300% → Chaque membre vient à 3 cultes en moyenne

---

## Conclusion

✅ **Le code est CONFORME à l'esprit du cahier des charges MDEVISP**

La formule implémentée est l'interprétation mathématiquement correcte des exigences du CDC.

**Pages concernées :**
- `/statistics/` → Statistiques générales avec graphiques
- `/mdevisp/` → Rapport MDEVISP officiel avec formules CDC
- `/mdevisp/annual/` → Rapport annuel consolidé

**Pour toute modification des formules, consulter l'administrateur système.**
