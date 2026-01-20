# SCHEMA JSON DNA - EXODUS SYSTEM
## Structure de données EXO_DATA_RAW.json

```json
{
  "session_id": "string",
  "timestamp": "ISO8601",
  "frame_number": "integer",
  "face_landmarks": {
    "upper_lip_center": {
      "x": "float 0.0-1.0",
      "y": "float 0.0-1.0",
      "z": "float",
      "landmark_id": 13
    },
    "lower_lip_center": {
      "x": "float 0.0-1.0",
      "y": "float 0.0-1.0",
      "z": "float",
      "landmark_id": 14
    },
    "mouth_open_ratio": "float 0.0-1.0",
    "all_468_landmarks": [
      {
        "x": "float",
        "y": "float",
        "z": "float",
        "landmark_id": "integer 0-467"
      }
    ]
  },
  "pose_landmarks": {
    "all_33_landmarks": [
      {
        "x": "float",
        "y": "float",
        "z": "float",
        "visibility": "float 0.0-1.0",
        "landmark_id": "integer 0-32"
      }
    ]
  },
  "optical_flow": {
    "magnitude": "float",
    "angle": "float radians",
    "flow_vectors": "array"
  },
  "audio_transcription": {
    "text": "string",
    "confidence": "float 0.0-1.0",
    "timestamp": "ISO8601"
  },
  "camera_metadata": {
    "fps": "float",
    "resolution": {
      "width": "integer",
      "height": "integer"
    }
  }
}
```

## Notes importantes

- **Landmarks 13-14 (PROTOCOLE INNER-LIP)** : Points critiques pour le calcul de l'ouverture de la bouche
  - Landmark 13 = `upper_lip_center` (centre de la lèvre supérieure - Inner Lip)
  - Landmark 14 = `lower_lip_center` (centre de la lèvre inférieure - Inner Lip)
  - **IMPORTANT** : Ces points ne sont PAS les coins de la bouche (corners). Les coins (61 et 291) sont inutiles pour le modèle Roblox simplifié.
  - `mouth_open_ratio` = distance verticale normalisée entre les deux points (0.0 = fermé, 1.0 = ouvert maximum)
  - Le calcul se base uniquement sur l'écartement vertical de ces deux points précis

- **Visual Tracking** : Utilisation de MediaPipe FaceMesh pour le tracking visuel (pas de phonèmes audio)

- **MediaPipe** : 
  - FaceMesh : 468 landmarks faciaux
  - Pose : 33 landmarks corporels

- **OpenCV Optical Flow** : Calcul du flux optique pour le mouvement de la caméra

- **Whisper** : Transcription audio locale (pas de dépendance cloud)

