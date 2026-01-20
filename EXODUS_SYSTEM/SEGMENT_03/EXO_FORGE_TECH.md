# 🛠️ NOTE TECHNIQUE (EXO_FORGE_TECH)

## Moteurs Principaux

### Blender 5.0
- **Rôle** : Moteur de rendu 3D
- **Usage** : Headless Python API pour automatisation
- **Version** : 5.0+ (dernière version stable)

### Cycles Engine
- **Rôle** : Ray Tracing
- **Usage** : Rendu photoréaliste avec éclairage avancé
- **Qualité** : Chef-d'œuvre

### FFmpeg
- **Rôle** : Post-production
- **Usage** : Fusion audio/vidéo, ajout logo, compression optimale

## Processus

### 1. Build_Scene
- Import automatique des modèles .glb
- Sources :
  - GitHub (repos publics)
  - Google Drive (dossiers partagés)
- Configuration de la scène :
  - Éclairage HDR
  - Caméra principale
  - Environnement

### 2. Apply_Motion
- Retargeting intelligent des mouvements du Segment 01
- Mapping des 33 points clés vers le rig Roblox
- Application des mouvements de caméra (zooms, pans)
- Synchronisation temporelle parfaite

### 3. Cine_Render
- Rendu 4K 60fps avec paramètres cinématographiques :
  - **Bloom** : Effet de lueur
  - **Motion Blur** : Flou de mouvement réaliste
  - **Depth of Field** : Profondeur de champ
- Cycles Engine avec échantillonnage élevé
- Export en séquence d'images ou vidéo brute

### 4. Post-Prod
- FFmpeg fusionne l'audio (`EXO_AUDIO_FINAL.mp3`)
- Ajout du logo **Blox Render 🧱🎬**
- Compression optimale pour YouTube
- Métadonnées et codec H.264/H.265

## Output

**Fichier** : `EXO_FINAL_RENDER.mp4`

**Spécifications** :
- Résolution : 4K (3840x2160)
- FPS : 60
- Codec : H.264 ou H.265
- Audio : AAC 48kHz
- Logo : Blox Render 🧱🎬 (coin inférieur)

## Nomenclature des Fichiers
- `EXO_FORGE_BUILD_SCENE_v1.0.py`
- `EXO_FORGE_APPLY_MOTION_v1.0.py`
- `EXO_FORGE_CINE_RENDER_v1.0.py`
- `EXO_FORGE_POST_PROD_v1.0.py`
- `EXO_FORGE_MAIN_v1.0.py`

