# 📜 CODEX EXODUS - L'OUTIL DE GUERRE

> **⚠️ RAPPEL DOCTRINAL :** Ce Codex est l'application de LA VOIE ROYALE à la niche Roblox US.  
> La Voie Royale est la doctrine suprême. Exodus n'est que l'armure pour cette bataille.

## NOMENCLATURE DU PROJET
**EXO_CORE**

## VISION
Transformer le génie viral du marché US en actifs 3D originaux 4K/60fps pour générer **300k USD/mois via le CPA**.

**OBJECTIF UNIQUE : 300 000 USD en 30 jours. Tout le reste est secondaire.**

## LE FLUX DE VIE

1. **SOURCING** (Humain) 
2. **DECONSTRUCTION** (Segment 01 - EXO_EYE)
3. **TRANSFIGURATION** (Segment 02 - EXO_CORTEX)
4. **SYNTHÈSE** (Segment 03 - EXO_FORGE)
5. **INFILTRATION** (Segment 04 - EXO_GHOST)

## ARCHITECTURE FANTÔME (V2 - PROTOCOLE BABEL)

### Langage Maître
- Python 3.10+

### Infrastructure
- Hybride : **Contrôle local** via Cursor / **Calcul Cloud** via Google Colab (Linux, GPU)

### Doctrine de l'Ancre Unique (`--drive-root`)
- Tous les segments parlent le **même langage de chemin** :
  - `--drive-root` pointe vers la racine EXODUS sur le disque (local ou Drive).
  - Si `--drive-root` est omis sous Colab, les scripts utilisent par défaut  
    `"/content/drive/MyDrive/EXODUS_SYSTEM"`.
- À partir de cette ancre, la structure est **standardisée** :
  - `00_INPUT/` : vidéos sources (.mp4)
  - `01_BUFFER/` : données intermédiaires (`mission_RAW.json`, `EXO_MISSION_READY.json`, audio normalisé, lip-sync)
  - `02_ASSETS/` :
    - `Avatars/` : `default.glb`, `actor_0.glb`, `actor_1.glb`, …
    - `Maps/` : décors `.glb` / `.fbx`
    - `Logos/` : `blox_render_logo.png`, autres overlays
  - `03_OUTPUT/` : rendus finaux (mp4, logs de rendu)
  - `04_TOOLS/` : outils binaires (Blender, Rhubarb, ffmpeg si besoin)
  - `05_CODEBASE/` : copie du repository Git clonée sur Drive

### Standard d'Échange
- Le **lien unique** entre les segments est la paire :
  - `mission_RAW.json` (sortie du Scanner Universel – Segment 01)
  - `EXO_MISSION_READY.json` (sortie du Cortex – Segment 02)
- **PROTOCOLE BABEL** : ces fichiers transportent des données **multi‑acteurs** et sont agnostiques au "style" (bagarre, danse, etc.).

### Nomenclature des Fichiers
- Format : `EXO_[SEGMENT]_[NOM]_[VERSION]` pour les scripts individuels.
- Fichiers pivots V2 :
  - `01_EYE_INQUISITION/EXO_01_DNA_SCANNER.py`
  - `02_ALPHARIUS_CORTEX/EXO_02_CORTEX_ADAPTER.py`
  - `03_LEGION_FORGE/EXO_03_BLENDER_WORKER.py`

### Sécurité
- Zéro lien entre les 10 chaînes
- Chaque mission est isolée
- Anonymat total

---

## SEGMENT 01 – L’ŒIL (SCANNER UNIVERSEL MULTI‑ACTEURS)

### Moteur de Vision
- Utilise `mediapipe.tasks.python.vision.PoseLandmarker` en mode **multi‑pose** :
  - `num_poses = 5` (capture jusqu’à 5 corps simultanés par frame).
  - `min_pose_detection_confidence ≈ 0.5`.
- Complété par **FaceMesh** pour mesurer l’ouverture de bouche (`mouth_open_ratio`) via les landmarks de la lèvre interne.

### Doctrine de Tracking (ID par Axe X)
- Pour chaque frame :
  - Tous les corps détectés sont collectés.
  - Chaque corps est représenté par la position X de son "centre" (ex. nez).
  - La liste est triée par X → **les IDs sont stables par rang** :
    - Acteur `"0"` = plus à gauche.
    - Acteur `"1"` = suivant, etc.
- Cette stratégie fournit un **tracking stable** sans recourir à un système complexe d’ID inter‑frame.

### Structure de Sortie (mission_RAW.json)
- Segment 01 écrit **dans `01_BUFFER/mission_RAW.json`** sous la forme :
  - `metadata` : infos vidéo (fps, résolution, durée, nombre max d’acteurs vus…)
  - `camera_motion` : flux optique global (pan / tilt / zoom theoriques)
  - `actors` : dictionnaire d’acteurs indexés par ID string `"0"`, `"1"`, …:
    - `pose_frames` : 33 landmarks par frame (squelette complet)
    - `mouth_frames` : `mouth_open_ratio` + timestamps

---

## SEGMENT 03 – LA FORGE (BLENDER WORKER LÉGIONNAIRE)

### Importation Dynamique des Avatars (Fallback Intelligent)
- Le Worker lit `EXO_MISSION_READY.json` et extrait les clés de `actors` :
  - ex. `["0", "1", "2"]`.
- Pour chaque ID `i` :
  - Tente de charger `02_ASSETS/Avatars/actor_{i}.glb`.
  - **Fallback** :
    - Si le fichier n’existe pas, charge `02_ASSETS/Avatars/default.glb`.
    - Si même `default.glb` est absent → **erreur** explicite (mission impossible).
- Chaque avatar importé est lié à une armature nommée :
  - `EXO_Avatar_{i}_Armature`

### Boucle d’Animation par Acteur
- Le Worker boucle sur `self.armatures_by_actor` :
  - Pour chaque `(actor_id, armature)` :
    - Récupère `mission_data["actors"][actor_id]["pose_frames"]`.
    - Convertit ces frames dans un format interne (frame_number + liste des landmarks).
    - Fait un **retargeting MediaPipe → bones Roblox** (bras, jambes, colonne).
    - Insère les keyframes de rotation pour chaque bone, frame par frame.
- Résultat : **chaque armature suit l’ADN de mouvement de son acteur** dans la vidéo source.

### Lip‑Sync Multi‑Source
- Le Worker combine deux sources potentielles :
  1. `mouth.mouthCues` (Rhubarb) – **global audio** (mode DRAMA).
  2. `actors["0"]["mouth_frames"]` – **mouth_open_ratio** (scanner brut) en fallback.
- La bouche de l’avatar (ShapeKey type `MouthOpen` / `Jaw` / etc.) est animée :
  - Soit par les **phonèmes Rhubarb**, soit par un **ratio continu** par frame.

---

## JSON – EXEMPLE SIMPLIFIÉ (PROTOCOLE BABEL)

```json
{
  "metadata": {
    "mission_id": "EXO_MISSION_20260120_153045",
    "mode": "DRAMA",
    "source_metadata": {
      "fps": 60,
      "resolution": [1080, 1920],
      "max_actors_detected": 2
    }
  },
  "camera_motion": [
    {
      "frame_number": 0,
      "timestamp": "2026-01-20T15:30:45.000Z",
      "vx": 0.01,
      "vy": -0.02,
      "magnitude": 0.03
    }
  ],
  "actors": {
    "0": {
      "pose_frames": [
        {
          "frame_number": 0,
          "timestamp": "2026-01-20T15:30:45.000Z",
          "center_x": 0.25,
          "landmarks": [
            { "landmark_id": 0, "x": 0.1, "y": 0.2, "z": -0.05, "visibility": 0.99 }
            // ...
          ]
        }
      ],
      "mouth_frames": [
        {
          "frame_number": 0,
          "timestamp": "2026-01-20T15:30:45.000Z",
          "mouth_open_ratio": 0.7
        }
      ]
    },
    "1": {
      "pose_frames": [
        {
          "frame_number": 0,
          "timestamp": "2026-01-20T15:30:45.000Z",
          "center_x": 0.75,
          "landmarks": [
            { "landmark_id": 0, "x": 0.8, "y": 0.2, "z": -0.04, "visibility": 0.98 }
            // ...
          ]
        }
      ],
      "mouth_frames": []
    }
  },
  "speech": {
    "original_text": "He punched me in Brookhaven...",
    "viral_text": "He cooked me in Ohio Brookhaven... W",
    "transformation_applied": true
  },
  "mouth": {
    "mouthCues": [
      { "start": 0.00, "end": 0.12, "value": "A" },
      { "start": 0.12, "end": 0.28, "value": "C" }
    ],
    "metadata": {
      "status": "rhubarb_generated"
    }
  },
  "global_audio_sync": {
    "primary_actor_id": "0",
    "lip_sync_status": "rhubarb_generated"
  }
}
```

## PHILOSOPHIE ALPHA LEGION
- **Anonymat** : Aucune trace, aucune signature (notre bouclier)
- **Efficacité** : Chaque ligne de code doit être optimale
- **Cash** : Notre épée. 300k USD/mois ou échec total
- **Vitesse** : Plus importante que l'élégance du code
- **Automatisation Totale** : Zéro intervention humaine après lancement

## SERVIR LA VOIE ROYALE
Ce Codex sert LA VOIE ROYALE. Il n'est qu'une application parmi d'autres possibles.

