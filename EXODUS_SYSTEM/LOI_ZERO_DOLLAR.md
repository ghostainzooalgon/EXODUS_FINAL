# 💰 LOI DU ZÉRO DOLLAR - DOCTRINE DE LA FORGE

## PRINCIPE SUPRÊME

**Tout composant d'EXODUS doit être Open-Source ou Freeware.**

Aucune API payante ne doit être intégrée au code final.

## RÈGLES ABSOLUES

### 1. ZÉRO API PAYANTE
- ❌ OpenAI API (payant)
- ❌ Claude API (payant)
- ❌ ElevenLabs API (payant)
- ❌ Toute API nécessitant une clé payante

### 2. UNIQUEMENT OPEN-SOURCE / FREEWARE
- ✅ Whisper LOCAL (library, pas API)
- ✅ OpenCV (Open Source)
- ✅ MediaPipe (Open Source Google)
- ✅ Rhubarb LipSync (Open Source)
- ✅ Blender (Open Source)
- ✅ FFmpeg (Open Source)

### 3. FONCTIONNEMENT AUTONOME
Le système doit être capable de fonctionner dans le "Warp" (Cloud gratuit) sans :
- Clé d'activation
- Abonnement
- Connexion internet (après téléchargement initial des modèles)

## APPLICATIONS PAR SEGMENT

### SEGMENT 01 (EXO_EYE)
- ✅ Whisper LOCAL (`pip install openai-whisper`)
- ✅ OpenCV (Open Source)
- ✅ MediaPipe (Open Source)
- ✅ Fonctionne entièrement hors ligne après installation

### SEGMENT 02 (EXO_CORTEX)
- ✅ Rhubarb LipSync (Open Source)
- ⚠️ Audio fourni par l'Empereur (généré en externe)
- ⚠️ Script fourni par l'Empereur (réécrit en externe)
- ✅ Le code ne fait QUE analyser et synchroniser

### SEGMENT 03 (EXO_FORGE)
- ✅ Blender 5.0 (Open Source)
- ✅ Cycles Engine (inclus dans Blender)
- ✅ FFmpeg (Open Source)
- ✅ Fonctionne entièrement hors ligne

### SEGMENT 04 (EXO_GHOST)
- ⚠️ Outils externes gérés par l'Empereur
- ✅ Le code gère uniquement l'automatisation locale

## VALIDATION

Avant chaque déploiement, vérifier :
1. ✅ Aucune clé API dans le code
2. ✅ Toutes les dépendances sont Open Source
3. ✅ Le système fonctionne sans connexion internet (après setup)
4. ✅ Test RAM passé sur système 8Go

## SANCTIONS

Tout code contenant des API payantes sera **IMMÉDIATEMENT PURGÉ**.

**La Voie Royale est mon guide, les 300k sont mon objectif.**

