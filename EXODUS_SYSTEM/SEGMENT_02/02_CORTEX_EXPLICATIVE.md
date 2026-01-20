# 📁 SEGMENT 02 : LE CORTEX D'ALPHARIUS (L'Adaptateur)

## 📘 NOTE EXPLICATIVE (02_CORTEX)

Ce segment est le maître du déguisement. Il prend les données brutes du Segment 01 et les "Américanise". 

**Principe Fondamental** : Il change le script pour qu'il soit toxique, viral et adapté au "Brain Rot" US.

### ⚠️ LOI DU ZÉRO DOLLAR APPLIQUÉE
- ❌ PURGÉ : Claude API (payant)
- ❌ PURGÉ : ElevenLabs API (payant)
- ✅ Rhubarb LipSync (Open Source)
- ⚠️ **L'Empereur fournira directement** :
  - Le script réécrit
  - Le fichier audio final (`EXO_AUDIO_FINAL.mp3`)

### Indépendance
Peut servir à analyser et synchroniser des podcasts ou des voix off sans vidéo.

### Objectif
Analyser l'audio fourni et générer la synchronisation labiale :
- Analyse phonétique de l'audio fourni
- Génération des mouvements de bouche via Rhubarb (Open Source)
- Synchronisation frame-perfect avec l'audio

### Entrée
- `EXO_DATA_RAW.json` (du Segment 01)
- `EXO_AUDIO_FINAL.mp3` (fourni par l'Empereur)

### Sortie
- `EXO_LIP_SYNC.json` (données de synchronisation labiale)

