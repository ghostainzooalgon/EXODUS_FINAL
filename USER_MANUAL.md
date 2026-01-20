# 🧭 USER_MANUAL – EXODUS SYSTEM (PROTOCOLE BABEL)

Ce manuel explique **comment un humain** installe et lance l’usine EXODUS sur Google Colab avec Google Drive.

La logique interne (multi‑acteurs, Blender, etc.) est déjà gérée par le code.  
Ici, tu apprends **quoi mettre où** et **quoi lancer**.

---

## 1. INSTALLATION – PRÉPARER L’ANCRE SUR GOOGLE DRIVE

1. Ouvre Google Drive.
2. Crée le dossier suivant à la racine de ton Drive (si ce n’est pas déjà fait) :
   - `MyDrive/EXODUS_SYSTEM`
3. À l’intérieur de `EXODUS_SYSTEM`, crée les sous‑dossiers (si absents) :
   - `00_INPUT/` – vidéos sources (tes mp4 à analyser)
   - `01_BUFFER/` – tampon technique (les JSON et audios intermédiaires)
   - `02_ASSETS/` – tous les assets graphiques/3D
   - `03_OUTPUT/` – sorties finales (les vidéos rendues)
   - `04_TOOLS/` – outils (Blender, Rhubarb, etc.)
   - `05_CODEBASE/` – copie du repository Git (le code Python)

4. Depuis GitHub, récupère le projet `EXODUS_SYSTEM` :
   - soit en le clonant dans `05_CODEBASE` depuis Colab (recommandé),
   - soit en le téléchargeant en `.zip` et en le déposant dans `05_CODEBASE` manuellement.

**Règle d’or :** `EXODUS_SYSTEM` sur Drive est **l’ancre**.  
Tous les scripts seront appelés avec `--drive-root "/content/drive/MyDrive/EXODUS_SYSTEM"`.

---

## 2. RAVITAILLEMENT – QUE METTRE DANS 00_INPUT ET 02_ASSETS

### 2.1. Dossier `00_INPUT` – Vidéos sources

Dans `EXODUS_SYSTEM/00_INPUT`, tu déposes tes vidéos :

- Formats recommandés : `.mp4`
- Orientation : idéalement vertical (1080x1920) pour Shorts
- Exemple :
  - `00_INPUT/brookhaven_fight_01.mp4`
  - `00_INPUT/brookhaven_reaction_02.mp4`

Le **Segment 01** (Scanner Universel) scannera ce dossier et générera les données brutes pour chaque vidéo.

### 2.2. Dossier `02_ASSETS` – Avatars, Maps, Logos

À l’intérieur de `EXODUS_SYSTEM/02_ASSETS`, structure recommandée :

- `Avatars/`
  - `default.glb` → avatar par défaut (utilisé si aucun avatar spécifique n’est trouvé).
  - `actor_0.glb` → avatar pour l’acteur ID `"0"`.
  - `actor_1.glb` → avatar pour l’acteur ID `"1"`.
  - `actor_2.glb`, … jusqu’à `actor_4.glb` (le système supporte jusqu’à 5 acteurs par vidéo).

- `Maps/`
  - Décors 3D (ex. `map_brookhaven.glb`), importés par le Segment 03.

- `Logos/`
  - `blox_render_logo.png` → logo overlay utilisé par la post‑prod (FFmpeg).

> Si un fichier `actor_i.glb` est manquant, le Segment 03 utilisera automatiquement `default.glb` comme fallback.  
> Si même `default.glb` est absent, la Forge arrêtera la mission pour éviter un rendu cassé.

---

## 3. LANCEMENT – UTILISER GOOGLE COLAB

### 3.1. Ouvrir le Notebook de Contrôle

1. Ouvre **Google Colab**.
2. Depuis Colab, va dans `File → Open notebook → Google Drive`.
3. Navigue jusqu’à ton dossier `EXODUS_SYSTEM` sur Drive.
4. Ouvre le fichier :
   - `EXODUS_ORCHESTRATOR.ipynb` (ou `EXO_LAUNCHER_COLAB.ipynb` selon ta version).

> Ce notebook est le **panneau de contrôle** : il monte le Drive, synchronise le code, installe les dépendances et appelle les segments.

### 3.2. Exécuter les cellules dans l’ordre

Selon la version de ton notebook :

1. **Montage du Drive**  
   - La cellule monte `'/content/drive'` et définit une variable du type :
     - `DRIVE_ROOT = "/content/drive/MyDrive/EXODUS_SYSTEM"`

2. **Synchronisation du Code**  
   - Le notebook :
     - soit clone le repo GitHub dans `05_CODEBASE`,
     - soit bascule dans le dossier déjà présent.

3. **Installation des dépendances**  
   - Cellule qui installe :
     - `mediapipe`, `opencv-python`, `openai-whisper`, `pydub`, etc.
     - `ffmpeg` via `apt-get`.

4. **Préparation de Blender**  
   - Définit un chemin :
     - `BLENDER_PATH = DRIVE_ROOT + "/04_TOOLS/blender-4.0.2-linux-x64/blender"`
   - Rend le binaire exécutable (`chmod +x`) et affiche la version.

5. **Lancement des Segments** (exemple logique)  
   - Le notebook appelle :
     - `EXO_01_DNA_SCANNER.py` avec `--drive-root "$DRIVE_ROOT"`
     - `EXO_02_CORTEX_ADAPTER.py` avec `--drive-root "$DRIVE_ROOT"`
     - `EXO_03_BLENDER_WORKER.py` via Blender :
       - `"$BLENDER_PATH" -b -P 03_LEGION_FORGE/EXO_03_BLENDER_WORKER.py -- --drive-root "$DRIVE_ROOT"`

> Vérifie que **chaque script** est bien lancé avec `--drive-root "$DRIVE_ROOT"`  
> pour que tous pointent sur **la même ancre** (`EXODUS_SYSTEM` sur ton Drive).

---

## 4. FLUX GLOBAL – CE QUI SE PASSE UNE FOIS LANCÉ

1. **Segment 01 – Scanner Universel**  
   - Lit les vidéos dans `00_INPUT/`.
   - Produit `01_BUFFER/mission_RAW.json` avec :
     - `camera_motion` (mouvements caméra bruts),
     - `actors["i"].pose_frames` et `actors["i"].mouth_frames`.

2. **Segment 02 – Cortex Adapter**  
   - Lit `01_BUFFER/mission_RAW.json`.
   - Applique la transformation de texte (Brain Rot) et le lip‑sync Rhubarb.
   - Écrit `01_BUFFER/EXO_MISSION_READY.json` (PROTOCOLE BABEL, multi‑acteurs).

3. **Segment 03 – Blender Worker**  
   - Lit `01_BUFFER/EXO_MISSION_READY.json`.
   - Importe les avatars depuis `02_ASSETS/Avatars/`.
   - Mappe chaque acteur sur son armature.
   - Rend les vidéos (avec overlay logo + post‑prod FFmpeg) dans `03_OUTPUT/`.

---

## 5. CHECKLIST RAPIDE AVANT LANCEMENT

- [ ] `EXODUS_SYSTEM/00_INPUT` contient au moins 1 `.mp4`.
- [ ] `EXODUS_SYSTEM/02_ASSETS/Avatars/default.glb` est présent.
- [ ] Blender 4.0.2 est bien présent dans `EXODUS_SYSTEM/04_TOOLS/` (ou installé par le notebook).
- [ ] Tu as ouvert le notebook sur Colab et exécuté **toutes les cellules** dans l’ordre.
- [ ] Les commandes de lancement des scripts passent bien `--drive-root "/content/drive/MyDrive/EXODUS_SYSTEM"`.

Si tout est vert, tu peux lancer la production.  
**La Voie Royale est ton guide.**


