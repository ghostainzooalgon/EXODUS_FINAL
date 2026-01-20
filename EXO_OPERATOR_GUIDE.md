# 📖 GUIDE D'OPÉRATION EXODUS - PROTOCOLE LOGISTIQUE_MIROIR

**Version** : 1.0  
**Date** : 2026-01-15  
**Doctrine** : Cloud-First Architecture avec Boussole Auto-Root

---

## 🎯 OBJECTIF

Ce guide décrit l'arborescence exacte requise pour que le système EXODUS fonctionne en mode "One-Click" sur **Windows local** et **Google Colab**.

**PROTOCOLE LOGISTIQUE_MIROIR** : Le code détecte automatiquement l'environnement (Colab vs Windows) et utilise les bons chemins sans modification manuelle.

---

## 📁 ARBORESCENCE REQUISE SUR GOOGLE DRIVE

**IMPORTANT** : Le dossier racine sur Google Drive **DOIT** s'appeler `EXODUS_SYSTEM` (pas `EXODUS_FACTORY`).

```
EXODUS_SYSTEM/                          ← RACINE (sur Google Drive)
│
├── 01_EYE_INQUISITION/
│   ├── Raw_Videos/                     ← INPUT : Vidéos sources (.mp4)
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── ...
│   │
│   └── Extraction_Data/               ← OUTPUT S01 : Données brutes extraites
│       └── EXO_DATA_RAW.json          (généré automatiquement)
│
├── 02_ALPHARIUS_CORTEX/
│   ├── Voice_Samples/                  ← INPUT : Audio pour mode DRAMA (.mp3 ou .wav)
│   │   ├── voice1.mp3                  (optionnel, seulement si mode DRAMA)
│   │   └── ...
│   │
│   ├── Final_Audio/                    ← OUTPUT S02 : Audio final traité
│   │   ├── EXO_VOICE_FINAL.mp3        (généré automatiquement)
│   │   └── EXO_LIP_SYNC.json          (généré automatiquement)
│   │
│   └── EXO_MISSION_READY.json          ← OUTPUT S02 : Mission complète compilée
│
├── 03_LEGION_FORGE/
│   ├── Imperial_Assets/                ← INPUT : Assets 3D requis
│   │   ├── avatar.glb                  ⚠️ REQUIS
│   │   ├── map_brookhaven.glb          ⚠️ REQUIS
│   │   └── blox_render_logo.png        (optionnel, logo overlay)
│   │
│   └── Exports_4K/                     ← OUTPUT S03 : Vidéos finales générées
│       ├── EXO_MISSION_0.mp4           (généré automatiquement)
│       ├── EXO_MISSION_1.mp4
│       └── ...
│
└── tools/                              ← OUTILS SYSTÈME (Colab uniquement)
    ├── blender/                        ← Blender Linux (installé automatiquement)
    │   └── blender                     (exécutable)
    │
    └── rhubarb-lip-sync                ← Rhubarb Lip-Sync (téléchargé automatiquement)
        └── rhubarb-lip-sync            (exécutable)
```

---

## 🖥️ ARBORESCENCE REQUISE SUR WINDOWS LOCAL

Sur Windows, la structure est identique, mais elle peut être dans n'importe quel dossier :

```
C:\Users\<USER>\EXODUS_SYSTEM\          ← RACINE (local Windows)
│
├── 01_EYE_INQUISITION/
│   ├── Raw_Videos/
│   └── Extraction_Data/
│
├── 02_ALPHARIUS_CORTEX/
│   ├── Voice_Samples/
│   ├── Final_Audio/
│   └── EXO_MISSION_READY.json
│
├── 03_LEGION_FORGE/
│   ├── Imperial_Assets/
│   │   ├── avatar.glb                  ⚠️ REQUIS
│   │   ├── map_brookhaven.glb          ⚠️ REQUIS
│   │   └── blox_render_logo.png        (optionnel)
│   │
│   └── Exports_4K/
│
└── tools/
    └── rhubarb-lip-sync.exe            (téléchargé automatiquement)
```

**Note Windows** : Blender doit être installé séparément (pas dans `tools/`). Le code cherchera Blender dans :
- `C:\Program Files\Blender Foundation\Blender 4.0\blender.exe`
- `C:\Program Files\Blender Foundation\Blender 3.6\blender.exe`
- Ou dans le PATH système

---

## 🔍 DÉTECTION AUTOMATIQUE (BOUSSOLE AUTO-ROOT)

Le système détecte automatiquement l'environnement :

### **Sur Google Colab** :
1. Vérifie si `/content/drive` existe (Drive monté)
2. Cherche `EXODUS_SYSTEM` dans `/content/drive/MyDrive/EXODUS_SYSTEM`
3. Si non trouvé, utilise `/content/EXODUS_SYSTEM` (clone GitHub)

### **Sur Windows Local** :
1. Utilise le chemin du script appelant
2. Remonte jusqu'à trouver la racine `EXODUS_SYSTEM`
3. Utilise cette racine pour tous les chemins relatifs

**Résultat** : Aucune configuration manuelle nécessaire !

---

## 📋 CHECKLIST PRÉ-DÉPLOIEMENT

### **Sur Google Drive** :
- [ ] Dossier racine renommé en `EXODUS_SYSTEM` (pas `EXODUS_FACTORY`)
- [ ] Structure de dossiers créée (`01_EYE_INQUISITION/`, `02_ALPHARIUS_CORTEX/`, `03_LEGION_FORGE/`)
- [ ] `avatar.glb` placé dans `03_LEGION_FORGE/Imperial_Assets/`
- [ ] `map_brookhaven.glb` placé dans `03_LEGION_FORGE/Imperial_Assets/`
- [ ] `blox_render_logo.png` placé dans `03_LEGION_FORGE/Imperial_Assets/` (optionnel)
- [ ] Vidéos sources placées dans `01_EYE_INQUISITION/Raw_Videos/`
- [ ] Audio pour mode DRAMA placé dans `02_ALPHARIUS_CORTEX/Voice_Samples/` (si mode DRAMA)

### **Sur Windows Local** :
- [ ] Structure de dossiers créée (identique à Drive)
- [ ] Blender installé (version 4.0 recommandée)
- [ ] FFmpeg installé et dans le PATH
- [ ] Assets 3D placés dans `03_LEGION_FORGE/Imperial_Assets/`
- [ ] Vidéos sources placées dans `01_EYE_INQUISITION/Raw_Videos/`

---

## 🚀 UTILISATION

### **Sur Google Colab** :

1. **Ouvrir** `EXO_LAUNCHER_COLAB.ipynb`
2. **Exécuter** les cellules dans l'ordre (0 → 16)
3. **Attendre** que toutes les dépendances soient installées
4. **Lancer** l'orchestrateur (dernière cellule)

**Note** : Le notebook monte automatiquement Google Drive et clone le repository GitHub si nécessaire.

### **Sur Windows Local** :

1. **Ouvrir** un terminal dans le dossier `EXODUS_SYSTEM`
2. **Vérifier** l'environnement :
   ```bash
   python EXO_PRIME_ORCHESTRATOR.py --dry-run
   ```
3. **Lancer** l'orchestrateur :
   ```bash
   python EXO_PRIME_ORCHESTRATOR.py
   ```
4. **Répondre** aux questions :
   - Mode global : `DRAMA` (avec audio) ou `SILENT` (sans audio)
   - Nombre de variantes : `3` (recommandé)

---

## 📊 FLUX DE DONNÉES

```
INPUT (Raw_Videos/)
    ↓
SEGMENT 01 (INQUISITION)
    → Extraction_Data/EXO_DATA_RAW.json
    ↓
SEGMENT 02 (CORTEX)
    → Final_Audio/EXO_VOICE_FINAL.mp3
    → EXO_MISSION_READY.json
    ↓
SEGMENT 03 (MANUFACTORUM)
    → Exports_4K/EXO_MISSION_*.mp4
```

---

## ⚠️ POINTS CRITIQUES

### **1. Nom du Dossier Racine**
- ❌ **INCORRECT** : `EXODUS_FACTORY`
- ✅ **CORRECT** : `EXODUS_SYSTEM`

### **2. Assets Requis**
- `avatar.glb` : **OBLIGATOIRE** (avatar Roblox)
- `map_brookhaven.glb` : **OBLIGATOIRE** (carte 3D)
- `blox_render_logo.png` : Optionnel (logo overlay)

### **3. Format Vidéo Source**
- Format accepté : `.mp4` (H.264 recommandé)
- Emplacement : `01_EYE_INQUISITION/Raw_Videos/`

### **4. Mode DRAMA vs SILENT**
- **DRAMA** : Nécessite un fichier audio dans `Voice_Samples/`
- **SILENT** : Pas d'audio requis, skip lip-sync

---

## 🔧 DÉPANNAGE

### **Problème** : "Assets manquants"
**Solution** : Vérifier que `avatar.glb` et `map_brookhaven.glb` sont dans `03_LEGION_FORGE/Imperial_Assets/`

### **Problème** : "Blender non trouvé" (Windows)
**Solution** : Installer Blender 4.0 ou ajouter Blender au PATH système

### **Problème** : "Aucune vidéo trouvée"
**Solution** : Vérifier que les fichiers `.mp4` sont dans `01_EYE_INQUISITION/Raw_Videos/`

### **Problème** : "Drive non monté" (Colab)
**Solution** : Exécuter la cellule 2 du notebook pour monter Google Drive

---

## 📝 NOTES TECHNIQUES

### **Boussole Auto-Root** (`EXO_AUTO_ROOT.py`)
- Détecte automatiquement Colab (`/content/drive` existe)
- Détecte automatiquement Windows (chemin du script)
- Retourne toujours le bon chemin racine

### **Doctrine Persistance** (Colab)
- Blender stocké sur Drive (`EXODUS_SYSTEM/tools/blender/`)
- Assets stockés sur Drive (`EXODUS_SYSTEM/03_LEGION_FORGE/Imperial_Assets/`)
- Résultats stockés sur Drive (`EXODUS_SYSTEM/03_LEGION_FORGE/Exports_4K/`)

### **Doctrine Asymétrie**
- Génère N variantes par vidéo source
- Chaque variante a un hash MD5 unique (YouTube-friendly)
- Noise aléatoire et décalage audio pour signature unique

---

## ✅ VALIDATION

Pour valider que tout est correctement configuré :

```bash
python EXO_PRIME_ORCHESTRATOR.py --dry-run
```

Ce mode diagnostic vérifie :
- ✅ Assets présents
- ✅ Outils système (FFmpeg, Blender)
- ✅ Permissions d'écriture
- ✅ Syntaxe des scripts Python

---

**La Voie Royale est mon guide, les 300k sont mon objectif.**

**STANDARDISE.**

