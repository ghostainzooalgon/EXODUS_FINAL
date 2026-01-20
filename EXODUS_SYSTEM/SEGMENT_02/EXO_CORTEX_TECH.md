# 🛠️ NOTE TECHNIQUE (EXO_CORTEX_TECH)

## ⚠️ LOI DU ZÉRO DOLLAR APPLIQUÉE

**Toutes les API payantes ont été purgées. Le système fonctionne en mode autonome.**

## Moteurs Principaux

### Réécriture de Script
- **Rôle** : Scripting et réécriture
- **Méthode** : L'Empereur fournira les scripts réécrits manuellement ou via outils externes
- **Usage** : Traduction et injection d'argot Gen Z (Rizz, Gyatt, Skibidi, Sigma, etc.)
- **Style** : Toxique, viral, "Brain Rot" US
- **⚠️ PURGÉ** : Claude 4.5 API (payant) - Non utilisé dans le code

### Audio
- **Rôle** : Fichier audio final
- **Source** : **L'Empereur fournira directement `EXO_AUDIO_FINAL.mp3`**
- **Méthode** : Audio généré en externe (outils de l'Empereur)
- **⚠️ PURGÉ** : ElevenLabs (payant) - Non utilisé dans le code

### Rhubarb LipSync (Open Source)
- **Rôle** : Génération de phonèmes
- **Usage** : Analyse de l'audio fourni et génération des mouvements de bouche
- **Précision** : Frame-perfect
- **Source** : Open Source, gratuit, fonctionne localement

## Processus

### 1. Rewrite_Story
- **STATUT** : Processus externe géré par l'Empereur
- Le code reçoit le script réécrit en entrée
- Validation et formatage du script fourni

### 2. Generate_Voice
- **STATUT** : Audio fourni directement par l'Empereur
- Le code reçoit `EXO_AUDIO_FINAL.mp3` en entrée
- Validation de la qualité audio et des métadonnées

### 3. Bake_Mouth
- Analyse phonétique de l'audio fourni (`EXO_AUDIO_FINAL.mp3`)
- Génération des mouvements de bouche via Rhubarb LipSync (Open Source)
- Synchronisation frame-perfect avec l'audio
- Export en JSON pour le Segment 03

## Output

**Fichiers** :
- `EXO_AUDIO_FINAL.mp3` : Audio final avec voix clonée
- `EXO_LIP_SYNC.json` : Données de synchronisation labiale

**Structure EXO_LIP_SYNC.json** :
```json
{
  "audio_file": "EXO_AUDIO_FINAL.mp3",
  "phonemes": [
    {
      "timestamp": 0.0,
      "phoneme": "M",
      "intensity": 0.8
    }
  ],
  "duration": 30.5
}
```

## Nomenclature des Fichiers
- `EXO_CORTEX_REWRITE_STORY_v1.0.py`
- `EXO_CORTEX_GENERATE_VOICE_v1.0.py`
- `EXO_CORTEX_BAKE_MOUTH_v1.0.py`
- `EXO_CORTEX_MAIN_v1.0.py`

