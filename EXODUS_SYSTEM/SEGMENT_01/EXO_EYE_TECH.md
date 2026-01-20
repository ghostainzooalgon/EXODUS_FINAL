# 🛠️ NOTE TECHNIQUE (EXO_EYE_TECH)

## Moteurs Principaux

### OpenCV
- **Rôle** : Vision et traitement d'image
- **Usage** : Décodage vidéo, Optical Flow, analyse de frames

### MediaPipe
- **Rôle** : Pose Tracking
- **Usage** : Extraction des 33 points clés du corps humain à 60fps
- **Points Clés** : Visage, mains, corps, posture complète

### OpenAI Whisper (LOCAL - ZÉRO COÛT)
- **Rôle** : Audio-to-Text
- **Usage** : Transcription précise avec timestamps millisecondes
- **Version** : Library locale (`pip install openai-whisper`) - **PAS d'API payante**
- **Modèle** : Whisper Large (téléchargé localement, gratuit et illimité)
- **Autonomie** : Fonctionne sans clé API, sans abonnement, sans connexion internet après téléchargement du modèle

## Processus

### 1. Scan_Motion
- Extrait 33 points clés du corps humain à 60fps
- Format de sortie : Array de coordonnées 3D par frame
- Référence temporelle : Timestamp absolu

### 2. Scan_Camera
- Analyse l'Optical Flow pour déduire :
  - Zooms (in/out)
  - Mouvements de caméra (pan, tilt, rotation)
  - Transitions et effets
- Sortie : Vecteurs de mouvement par frame

### 3. Scan_Dialogue
- Transcrit l'audio avec Whisper
- Génère des timestamps précis (millisecondes)
- Détecte les pauses, les intonations, les émotions

## Output

**Fichier** : `EXO_DATA_RAW.json`

**Structure** :
```json
{
  "metadata": {
    "source_video": "path/to/video.mp4",
    "fps": 60,
    "duration": 30.5,
    "resolution": "1920x1080"
  },
  "motion_data": {
    "frames": [
      {
        "timestamp": 0.0,
        "pose_keypoints": [...33 points...],
        "camera_motion": {...},
        "audio_segment": {...}
      }
    ]
  },
  "dialogue": [
    {
      "text": "...",
      "start": 0.0,
      "end": 2.5
    }
  ]
}
```

## Nomenclature des Fichiers
- `EXO_EYE_SCAN_MOTION_v1.0.py`
- `EXO_EYE_SCAN_CAMERA_v1.0.py`
- `EXO_EYE_SCAN_DIALOGUE_v1.0.py`
- `EXO_EYE_MAIN_v1.0.py`

