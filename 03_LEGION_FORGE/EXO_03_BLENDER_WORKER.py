#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXO_03_BLENDER_WORKER.py - Segment 03 : LEGION FORGE
Système EXODUS - Moteur de rendu Blender pour génération vidéo 4K/60fps

DOCTRINE :
- Exécution Blender Headless (Linux/Colab)
- Cloud-Agnostic (pathlib + --drive-root)
- Format Vertical Shorts (1080x1920)
- Cycles/Optix pour qualité chef-d'œuvre
"""

import bpy
import sys
import argparse
import subprocess
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import mathutils
from mathutils import Vector, Quaternion


class EXOForge:
    """
    Forge EXODUS - Moteur de rendu Blender pour génération vidéo finale
    """
    
    def __init__(self, drive_root: Optional[str] = None):
        """
        Initialise la Forge
        
        DOCTRINE DE L'ANCRE UNIQUE :
        - Si --drive-root fourni : Utilise ce chemin
        - Si absent (Défaut Colab) : Utilise /content/drive/MyDrive/EXODUS_SYSTEM
        
        Structure des sous-dossiers (basés sur la racine) :
        - 00_INPUT : Vidéos sources
        - 01_BUFFER : Données compilées (EXO_MISSION_READY.json, audio)
        - 02_ASSETS : Assets 3D (avatar.glb, map_brookhaven.glb, logo.png)
        - 03_OUTPUT : Exports vidéo finaux
        """
        # GESTION DES ARGUMENTS : Parser sys.argv après le séparateur --
        if drive_root is None:
            # Blender ajoute ses propres arguments, on ne lit que ce qui suit --
            if '--' in sys.argv:
                args_after_separator = sys.argv[sys.argv.index('--') + 1:]
                parser = argparse.ArgumentParser(description="EXO Blender Worker - Segment 03")
                parser.add_argument(
                    "--drive-root",
                    type=str,
                    default=None,
                    help="Racine du système de fichiers (ancre unique). Défaut: /content/drive/MyDrive/EXODUS_SYSTEM"
                )
                args = parser.parse_args(args_after_separator)
                drive_root = args.drive_root
        
        # DÉTERMINATION DE LA RACINE (L'ANCRE)
        if drive_root is None:
            # DÉFAUT COLAB : /content/drive/MyDrive/EXODUS_SYSTEM
            default_colab_root = Path("/content/drive/MyDrive/EXODUS_SYSTEM")
            if default_colab_root.exists():
                drive_root = str(default_colab_root)
                print(f"[INFO] Drive Root détecté automatiquement (Colab) : {drive_root}")
            else:
                # Fallback : détection depuis le script (environnement local)
                drive_root = str(Path(__file__).parent.parent.resolve())
                print(f"[WARNING] Colab non détecté, utilisation du chemin local : {drive_root}")
        else:
            print(f"[INFO] Drive Root fourni via argument : {drive_root}")
        
        # CONSTANTES DE CHEMINS (pathlib pour compatibilité Linux)
        self.drive_root = Path(drive_root)
        
        # LES SOUS-DOSSIERS (CONSTANTES) - Basés sur la racine
        self.INPUT_DIR = self.drive_root / "00_INPUT"
        self.DATA_DIR = self.drive_root / "01_BUFFER"
        self.ASSETS_DIR = self.drive_root / "02_ASSETS"
        self.OUTPUT_DIR = self.drive_root / "03_OUTPUT"
        
        # Chemins spécifiques (compatibilité avec le reste du code)
        self.segment02_dir = self.DATA_DIR  # Alias pour compatibilité
        self.mission_ready_path = self.DATA_DIR / "EXO_MISSION_READY.json"
        self.assets_dir = self.ASSETS_DIR  # Alias pour compatibilité
        self.exports_dir = self.OUTPUT_DIR  # Alias pour compatibilité
        # LEGION DYNAMIQUE : répertoires dédiés aux avatars multi-acteurs
        self.avatars_dir = self.ASSETS_DIR / "Avatars"
        self.armatures_by_actor: Dict[str, "bpy.types.Object"] = {}
        
        # Création des dossiers si nécessaire
        self.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Référence vers l'armature de l'avatar (sera définie lors de l'import)
        self.armature = None
        
        # Données de mission (sera chargé par load_mission_data)
        self.mission_data = None
        
        # VARIANTES (Doctrine Asymétrie) - Input Empereur
        self.num_variantes = 1  # Sera défini par input Empereur
        self.camera_intensity = 1.0  # Multiplicateur intensity pour caméra (variera par variante)
        
        # Référence caméra (sera créée dans setup_camera)
        self.camera = None
        
        # AFFICHAGE DES CHEMINS DÉTECTÉS (pour débuggage)
        print("=" * 80)
        print("[DOCTRINE DE L'ANCRE UNIQUE] - Chemins détectés :")
        print("=" * 80)
        print(f"  RACINE (ANCRE)     : {self.drive_root}")
        print(f"  INPUT_DIR          : {self.INPUT_DIR}")
        print(f"  DATA_DIR           : {self.DATA_DIR}")
        print(f"  ASSETS_DIR         : {self.ASSETS_DIR}")
        print(f"  OUTPUT_DIR         : {self.OUTPUT_DIR}")
        print(f"  Mission Ready      : {self.mission_ready_path}")
        print("=" * 80)

    def setup_scene(self):
        """
        Configure la scène Blender pour format Vertical Shorts
        
        Configuration :
        - Résolution : 1080x1920 (format vertical)
        - FPS : 60
        - Moteur : Cycles/Optix
        - Clean scene (suppression objets par défaut)
        - GPU Acceleration (CUDA/OPTIX)
        - Sortie vidéo FFmpeg (H.264)
        """
        print("[INFO] Configuration de la scène Blender...")
        
        # NETTOYAGE : Supprimer tous les objets par défaut
        print("[INFO] Nettoyage de la scène...")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Récupérer la scène active
        scene = bpy.context.scene
        
        # CONFIGURATION RENDU : Format Vertical Shorts
        print("[INFO] Configuration du format de rendu (1080x1920, 60fps)...")
        scene.render.resolution_x = 1080
        scene.render.resolution_y = 1920
        scene.render.resolution_percentage = 100
        scene.render.fps = 60
        scene.render.fps_base = 1.0
        
        # MOTEUR : CYCLES
        print("[INFO] Activation du moteur Cycles...")
        scene.render.engine = 'CYCLES'
        
        # Configuration Cycles
        cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
        scene.cycles.device = 'GPU'  # Tentative d'utilisation GPU
        
        # ACCÉLÉRATION MATÉRIELLE : Activation GPU (CUDA/OPTIX)
        print("[INFO] Détection et activation du GPU...")
        gpu_found = False
        
        try:
            # Forcer la détection des périphériques
            cycles_prefs.refresh_devices()
            
            # Accéder à la liste des périphériques (API Blender)
            # Note: cycles_prefs.devices est une liste, pas une méthode
            devices = cycles_prefs.devices
            
            # Activer tous les périphériques CUDA ou OPTIX
            for device in devices:
                device_type = device.type
                if device_type in ('CUDA', 'OPTIX'):
                    device.use = True
                    gpu_found = True
                    print(f"[SUCCESS] GPU activé : {device.name} ({device_type})")
                else:
                    device.use = False
            
            if gpu_found:
                # Forcer l'utilisation du GPU
                scene.cycles.device = 'GPU'
                print("[SUCCESS] Rendu GPU activé (CUDA/OPTIX)")
            else:
                print("[WARNING] Aucun GPU CUDA/OPTIX trouvé, fallback sur CPU")
                scene.cycles.device = 'CPU'
                # Activer tous les CPU disponibles
                for device in devices:
                    if device.type == 'CPU':
                        device.use = True
                        print(f"[INFO] CPU activé : {device.name}")
        
        except Exception as e:
            print(f"[WARNING] Erreur lors de la détection GPU : {e}")
            print("[INFO] Fallback sur CPU")
            scene.cycles.device = 'CPU'
        
        # Configuration qualité Cycles (High / Perceptually Lossless)
        scene.cycles.samples = 128  # Échantillonnage pour qualité élevée
        scene.cycles.use_denoising = True  # Dénuage pour qualité optimale
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        
        # MOTION BLUR (Qualité chef-d'œuvre)
        scene.render.use_motion_blur = True
        scene.render.motion_blur_shutter = 0.5  # Shutter speed (0.5 = motion blur modéré)
        print("[INFO] Motion Blur activé")
        
        # BLOOM (Post-processing - nécessite Compositing Nodes)
        # Note: Bloom dans Blender se fait via Compositing Nodes ou Eevee
        # Pour Cycles, on utilise les nodes de composition
        if scene.use_nodes is False:
            scene.use_nodes = True
        # Ajouter Bloom via Compositor (sera fait après setup)
        print("[INFO] Compositing Nodes activés pour Bloom")
        
        # SORTIE VIDÉO : Configuration FFmpeg
        print("[INFO] Configuration de la sortie vidéo FFmpeg...")
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        
        # Qualité High / Perceptually Lossless
        # CRF : 18 = High Quality (perceptually lossless), 23 = Default, 28 = Low
        scene.render.ffmpeg.constant_rate_factor = 'HIGH'  # Utilise la constante HIGH de Blender
        scene.render.ffmpeg.ffmpeg_preset = 'SLOW'  # Preset lent = meilleure compression
        
        # Configuration audio (si présent)
        scene.render.ffmpeg.audio_codec = 'AAC'
        scene.render.ffmpeg.audio_bitrate = 192
        
        print("[SUCCESS] Scène configurée avec succès")
        print(f"[INFO] Résolution : {scene.render.resolution_x}x{scene.render.resolution_y}")
        print(f"[INFO] FPS : {scene.render.fps}")
        print(f"[INFO] Moteur : {scene.render.engine}")
        print(f"[INFO] Périphérique : {scene.cycles.device}")
        print(f"[INFO] Format sortie : {scene.render.ffmpeg.format} ({scene.render.ffmpeg.codec})")

    def import_assets(self):
        """
        Importe les assets 3D depuis Assets_Bank
        
        Assets attendus :
        - map_brookhaven.glb (Décor statique)
        - avatar.glb (Avatar avec armature)  [LEGACY]

        LEGION DYNAMIQUE :
        - Le script détecte N acteurs depuis le JSON et importe N avatars :
          - ASSETS_DIR/Avatars/actor_{i}.glb (prioritaire)
          - sinon ASSETS_DIR/Avatars/default.glb (fallback)
          - si default.glb absent => erreur
        - Stocke les armatures dans self.armatures_by_actor["i"]
        
        CRITIQUE : Identifie et stocke la référence vers l'armature de l'avatar
        dans self.armature pour animation future.
        """
        print("[INFO] Import des assets 3D...")
        
        # IMPORT DU DÉCOR : map_brookhaven.glb
        decor_path = self.ASSETS_DIR / "map_brookhaven.glb"
        if not decor_path.exists():
            raise FileNotFoundError(
                f"[ERROR] Fichier décor introuvable : {decor_path}\n"
                f"Assurez-vous que map_brookhaven.glb est présent dans {self.ASSETS_DIR}"
            )
        
        print(f"[INFO] Import du décor : {decor_path.name}...")
        bpy.ops.import_scene.gltf(filepath=str(decor_path))
        
        # Marquer le décor comme statique (pas d'animation)
        # Les objets importés sont automatiquement sélectionnés
        for obj in bpy.context.selected_objects:
            obj.name = f"DECOR_{obj.name}"
            print(f"[INFO] Décor importé : {obj.name}")
        
        # ------------------------------
        # IMPORT DES AVATARS (LEGION DYNAMIQUE)
        # ------------------------------
        # Déterminer la liste des IDs d'acteurs depuis la mission, sinon fallback single actor "0"
        actor_ids: List[str] = []
        if self.mission_data and isinstance(self.mission_data.get("actors"), dict):
            actor_ids = list(self.mission_data["actors"].keys())
        elif self.mission_data and isinstance(self.mission_data.get("metadata", {}).get("actors"), dict):
            actor_ids = list(self.mission_data["metadata"]["actors"].keys())

        # Fallback : si le JSON ne contient pas d'actors, on importe un seul avatar
        if not actor_ids:
            actor_ids = ["0"]

        # Assurer que Avatars/ existe (mais ne pas le créer silencieusement : on veut signaler un mauvais layout)
        # On accepte cependant qu'il n'existe pas en mode legacy (avatar.glb à la racine ASSETS_DIR)
        default_avatar = self.avatars_dir / "default.glb"

        # Helper : importer un glb et retourner (armature, imported_objects)
        def _import_gltf(filepath: Path):
            bpy.ops.import_scene.gltf(filepath=str(filepath))
            imported = list(bpy.context.selected_objects)
            arm = None
            for o in imported:
                if o.type == "ARMATURE":
                    arm = o
                    break
            return arm, imported

        self.armatures_by_actor = {}

        # LEGACY PATH : si Avatars/default.glb n'existe pas et qu'on est en single actor,
        # on tente l'ancien ASSETS_DIR/avatar.glb
        legacy_avatar_path = self.ASSETS_DIR / "avatar.glb"

        for actor_id in actor_ids:
            actor_specific = self.avatars_dir / f"actor_{actor_id}.glb"
            chosen_path = None

            if actor_specific.exists():
                chosen_path = actor_specific
                print(f"[INFO] Avatar actor_{actor_id} détecté : {chosen_path.name}")
            elif default_avatar.exists():
                chosen_path = default_avatar
                print(f"[WARNING] Avatar actor_{actor_id} absent. Fallback → default.glb")
            elif legacy_avatar_path.exists() and actor_id == "0" and len(actor_ids) == 1:
                chosen_path = legacy_avatar_path
                print(f"[WARNING] Avatars/default.glb absent. Fallback legacy → {legacy_avatar_path.name}")
            else:
                raise FileNotFoundError(
                    f"[ERROR] Aucun avatar disponible pour actor_{actor_id}\n"
                    f"Attendu: {actor_specific} OU {default_avatar}\n"
                    f"(Fallback legacy single actor: {legacy_avatar_path})"
                )

            print(f"[INFO] Import avatar (actor {actor_id}) : {chosen_path}...")
            armature, imported_objects = _import_gltf(chosen_path)

            if armature is None:
                raise RuntimeError(
                    f"[ERROR] Aucune armature trouvée dans {chosen_path.name}\n"
                    "Chaque avatar .glb doit contenir un objet de type ARMATURE."
                )

            # Renommage pour éviter collisions
            armature.name = f"EXO_Avatar_{actor_id}_Armature"
            self.armatures_by_actor[str(actor_id)] = armature
            print(f"[SUCCESS] Armature actor {actor_id} : {armature.name}")

            for obj in imported_objects:
                if obj == armature:
                    continue
                if obj.type == "MESH":
                    obj.name = f"EXO_Avatar_{actor_id}_{obj.name}"
        
        # Compat legacy : self.armature pointe sur actor "0"
        self.armature = self.armatures_by_actor.get("0")
        
        print("[SUCCESS] Tous les assets importés avec succès")

    def setup_camera(self):
        """
        Configure la caméra procédurale
        
        Caméra optimisée pour format vertical 1080x1920
        Position : Hauteur d'yeux d'un avatar Roblox (Z=1.5m, Y=-3m)
        Focale : 35mm (standard TikTok/Shorts pour look dynamique)
        """
        print("[INFO] Configuration de la caméra...")
        
        # Créer une nouvelle caméra
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = 'EXO_Camera'
        
        # Position : Hauteur d'yeux Roblox (Z=1.5m, Y=-3m, X=0m)
        camera.location = (0.0, -3.0, 1.5)
        
        # Rotation : Regarder vers l'avant (légèrement vers le bas pour cadrage)
        camera.rotation_euler = (1.1, 0.0, 0.0)  # Pitch légèrement vers le bas
        
        # Focale : 35mm (standard TikTok/Shorts)
        camera.data.lens = 35.0
        camera.data.sensor_width = 36.0  # Format plein cadre (standard)
        
        # Définir comme caméra active de la scène
        scene = bpy.context.scene
        scene.camera = camera
        
        # Stocker la référence
        self.camera = camera
        
        print(f"[SUCCESS] Caméra configurée : {camera.name}")
        print(f"[INFO] Position : {camera.location}")
        print(f"[INFO] Focale : {camera.data.lens}mm")

    def apply_camera_animation(self, variant_id: int = 0):
        """
        DNA CAMERA MAPPING
        Mappe les vecteurs Optical Flow sur la caméra Blender
        
        Interdiction de créer de l'aléatoire : tout basé sur l'ADN de la vidéo source.
        Le multiplicateur intensity varie selon la variante (0.5x à 2.0x) pour rendre
        le mouvement plus ou moins nerveux, mais toujours basé sur les données source.
        
        Args:
            variant_id: ID de la variante (0 à N-1) pour calculer l'intensité
        """
        print(f"[INFO] DNA Camera Mapping (variante {variant_id})...")
        
        if self.mission_data is None:
            raise RuntimeError("[ERROR] Données de mission non chargées. Exécutez load_mission_data() d'abord.")
        
        if self.camera is None:
            raise RuntimeError("[ERROR] Caméra non trouvée. Exécutez setup_camera() d'abord.")
        
        # Calcul de l'intensité selon la variante (DOCTRINE ASYMÉTRIE)
        # Variante 0: 1.0x (base), Variante 1: 0.7x (calme), Variante 2: 1.3x (nerveux), etc.
        intensity_base = 1.0 + (variant_id % 3) * 0.3  # 1.0, 1.3, 1.6, puis retour à 1.0
        if variant_id % 3 == 1:
            intensity_base = 0.7  # Calme
        elif variant_id % 3 == 2:
            intensity_base = 1.5  # Nerveux
        
        self.camera_intensity = intensity_base
        print(f"[INFO] Intensité caméra : {self.camera_intensity}x")
        
        # Récupérer les données camera depuis mission_data
        camera_data = self.mission_data.get('camera', [])
        if not camera_data:
            print("[WARNING] Aucune donnée camera trouvée. Caméra statique.")
            return
        
        scene = bpy.context.scene
        fps = scene.render.fps
        
        # Position initiale de la caméra (base)
        base_location = Vector(self.camera.location)
        base_rotation = Vector(self.camera.rotation_euler)
        
        # Accumulateurs pour mouvement fluide (pas d'aléatoire, basé sur Optical Flow)
        cumulative_x = 0.0
        cumulative_y = 0.0
        cumulative_z = 0.0
        cumulative_rot_x = 0.0
        cumulative_rot_y = 0.0
        
        print(f"[INFO] Application de l'animation caméra sur {len(camera_data)} frames...")
        
        # BOUCLE TEMPORELLE : Pour chaque frame avec données optical_flow
        for frame_data in camera_data:
            frame_number = frame_data.get('frame_number', 0)
            optical_flow = frame_data.get('optical_flow', {})
            
            if not optical_flow:
                continue
            
            # Récupérer magnitude, angle et flow_vectors
            magnitude = optical_flow.get('magnitude', 0.0)
            angle = optical_flow.get('angle', 0.0)
            flow_vectors = optical_flow.get('flow_vectors', [])
            
            # Calculer la moyenne des vecteurs de flux (pour réduire le bruit)
            if flow_vectors:
                avg_x = sum(v[0] for v in flow_vectors) / len(flow_vectors)
                avg_y = sum(v[1] for v in flow_vectors) / len(flow_vectors)
            else:
                avg_x = 0.0
                avg_y = 0.0
            
            # Appliquer le multiplicateur d'intensité (variation par variante)
            scaled_x = avg_x * self.camera_intensity * 0.1  # Facteur d'échelle (0.1 pour éviter mouvements trop brusques)
            scaled_y = avg_y * self.camera_intensity * 0.1
            
            # Accumuler le mouvement (mouvement fluide, pas de sauts)
            cumulative_x += scaled_x
            cumulative_y += scaled_y
            cumulative_z += magnitude * self.camera_intensity * 0.01  # Légère variation Z basée sur magnitude
            
            # Rotation basée sur l'angle (mouvement de caméra pan/tilt)
            rot_x = (angle - 3.14159) * 0.05 * self.camera_intensity  # Normalisation angle (0 à 2π)
            rot_y = magnitude * 0.02 * self.camera_intensity
            
            cumulative_rot_x += rot_x * 0.1  # Lissage rotation
            cumulative_rot_y += rot_y * 0.1
            
            # Définir la frame
            scene.frame_set(frame_number)
            
            # Appliquer la position (base + mouvement accumulé)
            new_location = Vector((
                base_location.x + cumulative_x,
                base_location.y + cumulative_y,
                base_location.z + cumulative_z
            ))
            self.camera.location = new_location
            
            # Appliquer la rotation (base + rotation accumulée)
            new_rotation = Vector((
                base_rotation.x + cumulative_rot_x,
                base_rotation.y + cumulative_rot_y,
                base_rotation.z
            ))
            self.camera.rotation_euler = new_rotation
            
            # Insérer les keyframes
            self.camera.keyframe_insert(data_path="location", frame=frame_number)
            self.camera.keyframe_insert(data_path="rotation_euler", frame=frame_number)
        
        print(f"[SUCCESS] Animation caméra appliquée (intensité: {self.camera_intensity}x)")

    def setup_lighting(self):
        """
        Configure l'éclairage procédural "Studio"
        
        Éclairage à trois points (Key, Fill, Rim) :
        - Key Light : Area Light principale (côté, hauteur, puissante)
        - Fill Light : Area Light de débouchage (côté opposé, plus douce, teinte bleutée)
        - Rim Light : Point Light arrière (détache l'avatar, teinte rose/violette style Brookhaven)
        """
        print("[INFO] Configuration de l'éclairage studio...")
        
        # KEY LIGHT : Lumière principale (Area Light)
        print("[INFO] Création de la Key Light...")
        bpy.ops.object.light_add(type='AREA', location=(3.0, -2.0, 2.5))
        key_light = bpy.context.active_object
        key_light.name = 'EXO_KeyLight'
        key_light.data.energy = 50.0  # Puissante
        key_light.data.size = 2.0  # Grande surface pour lumière douce
        key_light.data.color = (1.0, 0.95, 0.9)  # Légèrement chaud
        key_light.rotation_euler = (-0.5, 0.3, 0.0)  # Orientée vers l'avatar
        print(f"[SUCCESS] Key Light créée : {key_light.name} (Energy: {key_light.data.energy})")
        
        # FILL LIGHT : Lumière de débouchage (Area Light)
        print("[INFO] Création de la Fill Light...")
        bpy.ops.object.light_add(type='AREA', location=(-3.0, -2.0, 1.5))
        fill_light = bpy.context.active_object
        fill_light.name = 'EXO_FillLight'
        fill_light.data.energy = 20.0  # Plus douce que la Key
        fill_light.data.size = 1.5
        fill_light.data.color = (0.85, 0.9, 1.0)  # Teinte bleutée
        fill_light.rotation_euler = (-0.3, -0.3, 0.0)  # Orientée vers l'avatar
        print(f"[SUCCESS] Fill Light créée : {fill_light.name} (Energy: {fill_light.data.energy})")
        
        # RIM LIGHT : Lumière arrière (Point Light)
        print("[INFO] Création de la Rim Light...")
        bpy.ops.object.light_add(type='POINT', location=(0.0, 2.0, 2.0))
        rim_light = bpy.context.active_object
        rim_light.name = 'EXO_RimLight'
        rim_light.data.energy = 30.0
        rim_light.data.color = (1.0, 0.7, 0.9)  # Teinte rose/violette (style Brookhaven)
        rim_light.data.shadow_soft_size = 0.5
        print(f"[SUCCESS] Rim Light créée : {rim_light.name} (Energy: {rim_light.data.energy})")
        
        print("[SUCCESS] Éclairage studio configuré avec succès")

    def load_mission_data(self):
        """
        Charge les données de mission depuis EXO_MISSION_READY.json
        
        Vérifie la présence des clés 'motion' et 'mouth'
        Stocke les données dans self.mission_data
        """
        print("[INFO] Chargement des données de mission...")
        
        if not self.mission_ready_path.exists():
            raise FileNotFoundError(
                f"[ERROR] Fichier mission introuvable : {self.mission_ready_path}"
            )
        
        with open(self.mission_ready_path, 'r', encoding='utf-8') as f:
            self.mission_data = json.load(f)
        
        # Vérification des blocs requis (PROTOCOLE BABEL)
        if 'actors' not in self.mission_data:
            raise KeyError("[ERROR] Clé 'actors' absente du fichier mission (PROTOCOLE BABEL)")
        
        actors = self.mission_data.get("actors", {})
        camera_motion = self.mission_data.get("camera_motion", [])
        
        print(f"[SUCCESS] Données de mission chargées (PROTOCOLE BABEL)")
        print(f"[INFO] Acteurs : {len(actors.keys())}")
        print(f"[INFO] Frames camera_motion : {len(camera_motion)}")

    def apply_animation(self):
        """
        Applique les animations depuis EXO_MISSION_READY.json
        
        Retargeting MediaPipe Pose vers bones Roblox :
        - Mode Pose activé
        - Mapping MediaPipe landmarks → bones
        - Calcul des rotations quaternion
        - Application frame par frame avec keyframes
        """
        print("[INFO] Application des animations...")
        
        if not self.armatures_by_actor:
            # Compat legacy (ancien comportement)
            if self.armature is None:
                raise RuntimeError("[ERROR] Armature non trouvée. Exécutez import_assets() d'abord.")
            self.armatures_by_actor = {"0": self.armature}
        
        if self.mission_data is None:
            raise RuntimeError("[ERROR] Données de mission non chargées. Exécutez load_mission_data() d'abord.")
        
        # MAPPING : Correspondance MediaPipe landmarks → bones Roblox
        # Format: 'BoneName': (landmark_start_id, landmark_end_id)
        # MediaPipe Pose landmarks: 0=nose, 5=left_shoulder, 6=right_shoulder, etc.
        bone_mapping = {
            # Bras gauche
            'LeftUpperArm': (5, 7),   # Épaule gauche (5) → Coude gauche (7)
            'LeftLowerArm': (7, 9),   # Coude gauche (7) → Poignet gauche (9)
            # Bras droit
            'RightUpperArm': (6, 8),  # Épaule droite (6) → Coude droit (8)
            'RightLowerArm': (8, 10),  # Coude droit (8) → Poignet droit (10)
            # Jambe gauche
            'LeftUpperLeg': (11, 13), # Hanche gauche (11) → Genou gauche (13)
            'LeftLowerLeg': (13, 15),  # Genou gauche (13) → Cheville gauche (15)
            # Jambe droite
            'RightUpperLeg': (12, 14), # Hanche droite (12) → Genou droit (14)
            'RightLowerLeg': (14, 16), # Genou droit (14) → Cheville droite (16)
            # Torse (optionnel)
            'Spine': (11, 0),  # Hanches → Tête (approximation)
        }
        
        # Helper : appliquer une animation à UNE armature à partir d'une liste motion_data
        def _apply_animation_to_armature(target_armature, motion_data):
            # Mode POSE : Activer le mode pose pour l'armature
            bpy.context.view_layer.objects.active = target_armature
            bpy.ops.object.mode_set(mode='POSE')

            # Récupérer les bones
            pose_bones = target_armature.pose.bones
        
        # Fonction helper pour trouver un landmark par ID
        def find_landmark(landmarks, landmark_id):
            """Trouve un landmark par son ID"""
            for landmark in landmarks:
                if landmark.get('landmark_id') == landmark_id:
                    return landmark
            return None
        
        # Fonction helper pour calculer la rotation quaternion
        def calculate_bone_rotation(start_landmark, end_landmark, bone_default_dir):
            """
            Calcule la rotation quaternion pour aligner un bone sur un vecteur
            
            Args:
                start_landmark: Landmark de départ (dict avec x, y, z)
                end_landmark: Landmark d'arrivée (dict avec x, y, z)
                bone_default_dir: Direction par défaut du bone (Vector)
            
            Returns:
                Quaternion de rotation
            """
            if start_landmark is None or end_landmark is None:
                return None
            
            # Vecteur directeur MediaPipe (Point_B - Point_A)
            mp_vector = Vector((
                end_landmark['x'] - start_landmark['x'],
                end_landmark['y'] - start_landmark['y'],
                end_landmark['z'] - start_landmark['z']
            ))
            
            # Normaliser
            if mp_vector.length == 0:
                return None
            
            mp_vector.normalize()
            
            # Direction par défaut du bone (normalisée)
            bone_dir = bone_default_dir.normalized()
            
            # Calculer la rotation pour aligner bone_dir sur mp_vector
            # Utiliser rotation_difference pour obtenir le quaternion
            try:
                rotation = bone_dir.rotation_difference(mp_vector)
                return rotation
            except:
                # Fallback : rotation identité si échec
                return Quaternion((1, 0, 0, 0))
        
            # Lissage simple (moyenne mobile sur 3 frames)
            previous_rotations = {}

            total_frames = len(motion_data)
            print(f"[INFO] Application de l'animation sur {total_frames} frames → {target_armature.name}")

            for frame_idx, frame_data in enumerate(motion_data):
                frame_number = frame_data.get('frame_number', frame_idx)
                pose_landmarks = frame_data.get('pose_landmarks', [])

                bpy.context.scene.frame_set(frame_number)

                for bone_name, (start_id, end_id) in bone_mapping.items():
                    if bone_name not in pose_bones:
                        bone_found = None
                        for variant in [bone_name, bone_name.lower(), bone_name.upper(),
                                       f"Left{bone_name}", f"Right{bone_name}"]:
                            if variant in pose_bones:
                                bone_found = variant
                                break
                        if bone_found is None:
                            continue
                        bone_name = bone_found

                    bone = pose_bones[bone_name]

                    start_landmark = find_landmark(pose_landmarks, start_id)
                    end_landmark = find_landmark(pose_landmarks, end_id)

                    if start_landmark and start_landmark.get('visibility', 0) < 0.5:
                        continue
                    if end_landmark and end_landmark.get('visibility', 0) < 0.5:
                        continue

                    bone_default_dir = (bone.tail - bone.head).normalized()
                    if bone_default_dir.length == 0:
                        bone_default_dir = Vector((0, 1, 0))

                    rotation = calculate_bone_rotation(start_landmark, end_landmark, bone_default_dir)
                    if rotation is None:
                        continue

                    if bone_name in previous_rotations:
                        prev_rot = previous_rotations[bone_name]
                        rotation = prev_rot.slerp(rotation, 0.7)

                    bone.rotation_quaternion = rotation
                    bone.keyframe_insert(data_path="rotation_quaternion", frame=frame_number)
                    previous_rotations[bone_name] = rotation

            bpy.ops.object.mode_set(mode='OBJECT')
            return total_frames

        total_applied = 0
        for actor_id, arm in self.armatures_by_actor.items():
            # BABEL : lecture directe de mission_data["actors"][id]["pose_frames"]
            motion_for_actor = []
            actors_block = self.mission_data.get("actors", {})
            actor_data = actors_block.get(str(actor_id), {})
            for pose_frame in actor_data.get("pose_frames", []):
                # Adapter au format attendu par _apply_animation_to_armature
                motion_for_actor.append(
                    {
                        "frame_number": pose_frame.get("frame_number", 0),
                        "pose_landmarks": pose_frame.get("landmarks", []),
                    }
                )

            total_applied = max(total_applied, _apply_animation_to_armature(arm, motion_for_actor))

        print(f"[SUCCESS] Animation appliquée (LEGION DYNAMIQUE) sur {len(self.armatures_by_actor)} acteur(s)")

    def apply_lip_sync(self):
        """
        Applique la synchronisation labiale
        
        Lecture des mouthCues depuis EXO_MISSION_READY.json
        et animation des ShapeKeys de la bouche
        
        Supporte deux modes :
        - mouthCues (Rhubarb) : valeurs A, B, C, E, F, X
        - mouth_open_ratio : valeur continue 0.0-1.0
        """
        print("[INFO] Application du lip-sync...")
        
        if self.mission_data is None:
            raise RuntimeError("[ERROR] Données de mission non chargées. Exécutez load_mission_data() d'abord.")
        
        # Trouver le mesh de l'avatar avec ShapeKeys
        avatar_mesh = None
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name.startswith('EXO_Avatar_'):
                if obj.data.shape_keys:
                    avatar_mesh = obj
                    break
        
        if avatar_mesh is None:
            print("[WARNING] Aucun mesh avatar avec ShapeKeys trouvé. Lip-sync ignoré.")
            return
        
        print(f"[INFO] Mesh avatar trouvé : {avatar_mesh.name}")
        
        # Récupérer les ShapeKeys
        shape_keys = avatar_mesh.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        # Mapping des valeurs Rhubarb vers ShapeKeys
        # Noms possibles : 'MouthOpen', 'O', 'Jaw', 'Mouth_A', 'Mouth_B', etc.
        mouth_shape_key = None
        possible_names = ['MouthOpen', 'O', 'Jaw', 'Mouth_Open', 'mouth_open', 'MouthOpen']
        
        for name in possible_names:
            if name in key_blocks:
                mouth_shape_key = key_blocks[name]
                print(f"[INFO] ShapeKey trouvé : {name}")
                break
        
        if mouth_shape_key is None:
            print("[WARNING] Aucun ShapeKey de bouche trouvé. Noms recherchés : " + ", ".join(possible_names))
            # Essayer de trouver n'importe quel ShapeKey contenant "mouth" ou "Mouth"
            for key_name in key_blocks.keys():
                if 'mouth' in key_name.lower() or 'jaw' in key_name.lower():
                    mouth_shape_key = key_blocks[key_name]
                    print(f"[INFO] ShapeKey alternatif trouvé : {key_name}")
                    break
        
        if mouth_shape_key is None:
            print("[ERROR] Impossible de trouver un ShapeKey pour la bouche")
            return
        
        # Récupérer les données mouth (PROTOCOLE BABEL)
        # Deux sources possibles :
        # - Rhubarb (mouthCues globaux)
        # - mouth_open_ratio par acteur dans mission_data["actors"][id]["mouth_frames"]
        mouth_data = self.mission_data.get('mouth', {})
        mouth_cues = mouth_data.get('mouthCues', [])
        
        # Mapping des valeurs Rhubarb vers ratios
        # A=fermé, B=mi-ouvert, C=ouvert, E=large, F=fermé serré, X=fermé
        rhubarb_to_ratio = {
            'A': 0.1,  # Fermé
            'B': 0.4,  # Mi-ouvert
            'C': 0.7,  # Ouvert
            'E': 0.9,  # Large
            'F': 0.2,  # Fermé serré
            'X': 0.0,  # Fermé
        }
        
        scene = bpy.context.scene
        fps = scene.render.fps
        
        applied_anything = False

        # 1) Si Rhubarb est présent → priorité (audio global)
        if mouth_cues:
            print(f"[INFO] Application de {len(mouth_cues)} mouth cues (Rhubarb)...")
            
            for cue in mouth_cues:
                start_time = cue.get('start', 0.0)
                end_time = cue.get('end', start_time)
                value = cue.get('value', 'X')
                
                # Convertir temps en frames
                start_frame = int(start_time * fps)
                end_frame = int(end_time * fps)
                
                # Ratio d'ouverture
                ratio = rhubarb_to_ratio.get(value, 0.0)
                
                # Appliquer sur la plage de frames
                for frame in range(start_frame, end_frame + 1):
                    scene.frame_set(frame)
                    mouth_shape_key.value = ratio
                    mouth_shape_key.keyframe_insert(data_path="value", frame=frame)
            
            applied_anything = True
        
        # 2) Sinon, fallback sur mouth_open_ratio de l'acteur 0 (SCANNER UNIVERSEL)
        if not applied_anything:
            actors_block = self.mission_data.get("actors", {})
            actor0 = actors_block.get("0", {})
            mouth_frames = actor0.get("mouth_frames", [])
            if mouth_frames:
                print(f"[INFO] Lip-sync via mouth_open_ratio pour l'acteur 0 ({len(mouth_frames)} frames)...")
                for mf in mouth_frames:
                    frame_number = mf.get("frame_number", 0)
                    ratio = float(mf.get("mouth_open_ratio", 0.0))
                    scene.frame_set(frame_number)
                    mouth_shape_key.value = ratio
                    mouth_shape_key.keyframe_insert(data_path="value", frame=frame_number)
                applied_anything = True
        
        if not applied_anything:
            print("[WARNING] Aucune donnée de lip-sync appliquée (Rhubarb ni mouth_open_ratio)")
        else:
            print("[SUCCESS] Lip-sync appliqué avec succès")

    def render_video(self, variant_id: int = 0):
        """
        Configure le rendu et lance l'export vidéo
        
        Configuration FFmpeg pour export MP4 4K/60fps
        Gestion de l'audio et synchronisation avec l'animation
        """
        print("[INFO] Configuration du rendu...")
        
        if self.mission_data is None:
            raise RuntimeError("[ERROR] Données de mission non chargées. Exécutez load_mission_data() d'abord.")
        
        scene = bpy.context.scene
        
        # 1. GESTION DE L'AUDIO (VITAL)
        print("[INFO] Configuration de l'audio...")
        
        # Créer le sequence_editor s'il n'existe pas
        if scene.sequence_editor is None:
            scene.sequence_editor_create()
            print("[INFO] Sequence editor créé")
        
        # Récupérer le chemin du fichier audio
        audio_path = None
        
        # Essayer depuis mouth.metadata.soundFile
        mouth_metadata = self.mission_data.get('mouth', {}).get('metadata', {})
        if 'soundFile' in mouth_metadata:
            audio_path = Path(mouth_metadata['soundFile'])
            if not audio_path.exists():
                # Convertir chemin Windows en chemin relatif si nécessaire
                audio_path = None
        
        # Essayer depuis Final_Audio/EXO_VOICE_FINAL.mp3 (chemin par défaut)
        if audio_path is None or not audio_path.exists():
            default_audio = self.segment02_dir / "Final_Audio" / "EXO_VOICE_FINAL.mp3"
            if default_audio.exists():
                audio_path = default_audio
                print(f"[INFO] Audio trouvé (chemin par défaut) : {audio_path}")
            else:
                # Essayer Voice_Samples/
                voice_samples = list((self.segment02_dir / "Voice_Samples").glob("*.mp3"))
                voice_samples.extend(list((self.segment02_dir / "Voice_Samples").glob("*.wav")))
                if voice_samples:
                    audio_path = voice_samples[0]
                    print(f"[INFO] Audio trouvé (Voice_Samples) : {audio_path}")
        
        # Ajouter l'audio à la timeline si trouvé
        if audio_path and audio_path.exists():
            print(f"[INFO] Ajout de l'audio à la timeline : {audio_path.name}")
            
            # Nettoyer les séquences audio existantes (éviter les doublons)
            sequences_to_remove = [seq for seq in scene.sequence_editor.sequences if seq.type == 'SOUND']
            for seq in sequences_to_remove:
                scene.sequence_editor.sequences.remove(seq)
            
            # Ajouter le nouveau fichier audio
            sound_strip = scene.sequence_editor.sequences.new_sound(
                name="EXO_Audio",
                filepath=str(audio_path.resolve()),
                channel=1,
                frame_start=1
            )
            
            # Obtenir la durée de l'audio en frames
            audio_duration_frames = sound_strip.frame_final_duration
            print(f"[INFO] Durée audio : {audio_duration_frames} frames ({audio_duration_frames / scene.render.fps:.2f}s)")
        else:
            print("[WARNING] Aucun fichier audio trouvé. Rendu sans audio.")
            audio_duration_frames = 0
        
        # 2. AJUSTER LA DURÉE DE LA SCÈNE
        # La fin de l'animation doit correspondre à la fin de l'audio ou des mouvements
        motion_data = self.mission_data.get('motion', [])
        if motion_data:
            last_frame = max(frame.get('frame_number', 0) for frame in motion_data)
            motion_end_frame = last_frame + 1  # +1 car frame_number commence à 0
        else:
            motion_end_frame = 1
        
        # Prendre le maximum entre audio et animation
        scene_end_frame = max(audio_duration_frames, motion_end_frame)
        
        scene.frame_start = 1
        scene.frame_end = scene_end_frame
        
        print(f"[INFO] Durée de la scène : {scene_end_frame} frames ({scene_end_frame / scene.render.fps:.2f}s)")
        print(f"[INFO] Frame start : {scene.frame_start}, Frame end : {scene.frame_end}")
        
        # 3. CONFIGURATION DE SORTIE (nom unique par variante)
        mission_id = self.mission_data.get('metadata', {}).get('mission_id', 'EXO_MISSION_UNKNOWN')
        output_filename = f"EXO_MISSION_{variant_id:03d}.mp4"
        output_path = self.OUTPUT_DIR / output_filename
        
        # Assurer que le dossier de sortie existe
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configurer le chemin de sortie
        scene.render.filepath = str(output_path.parent / output_path.stem)
        # Blender ajoutera automatiquement l'extension selon le format
        
        print(f"[INFO] Chemin de sortie : {output_path}")
        
        # 4. L'ORDRE DE TIR : Lancer le rendu
        print("=" * 60)
        print("[INFO] Début du rendu de l'animation...")
        print(f"[INFO] Résolution : {scene.render.resolution_x}x{scene.render.resolution_y}")
        print(f"[INFO] FPS : {scene.render.fps}")
        print(f"[INFO] Frames : {scene.frame_start} → {scene.frame_end} ({scene_end_frame} frames)")
        print(f"[INFO] Format : {scene.render.ffmpeg.format} ({scene.render.ffmpeg.codec})")
        print("=" * 60)
        
        try:
            # Lancer le rendu de l'animation complète
            bpy.ops.render.render(animation=True)
            
            print("=" * 60)
            print(f"[SUCCESS] Rendu terminé avec succès !")
            print(f"[SUCCESS] Fichier généré : {output_path}")
            print("=" * 60)
            
            # Vérifier que le fichier existe
            if output_path.exists():
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"[INFO] Taille du fichier : {file_size_mb:.2f} MB")
            else:
                # Blender peut créer le fichier avec une extension différente
                possible_outputs = list(output_path.parent.glob(f"{output_path.stem}*"))
                if possible_outputs:
                    actual_output = possible_outputs[0]
                    print(f"[INFO] Fichier trouvé : {actual_output.name}")
                    print(f"[INFO] Taille : {actual_output.stat().st_size / (1024 * 1024):.2f} MB")
        
        except Exception as e:
            print(f"[ERROR] Erreur lors du rendu : {e}")
            import traceback
            traceback.print_exc()
            # Retourner le chemin attendu même en cas d'erreur (pour continuer)
            return output_path
        
        # Retourner le chemin du fichier rendu pour post-prod
        return output_path

    def post_prod_ghost(self, rendered_video_path: Path, variant_id: int = 0):
        """
        POST-PROD GHOST (FFMPEG)
        
        Tâche A : Fusion image (Blender) + son (ElevenLabs/fichier audio)
        Tâche B : Incrustation du logo Blox Render 🧱🎬
        Tâche C (Unique Signature) : Pour chaque variante, injecte un filtre noise
        aléatoire à 0.5% et décale l'audio de 0.01s. Chaque fichier doit avoir un Hash
        différent pour YouTube.
        
        Args:
            rendered_video_path: Chemin vers la vidéo rendue par Blender
            variant_id: ID de la variante (pour noise unique)
        
        Returns:
            Chemin vers le fichier final post-produit
        """
        print(f"[INFO] Post-Prod Ghost (variante {variant_id})...")
        
        # Trouver le fichier audio source
        audio_path = None
        mouth_metadata = self.mission_data.get('mouth', {}).get('metadata', {})
        if 'soundFile' in mouth_metadata:
            audio_path = Path(mouth_metadata['soundFile'])
            if not audio_path.exists():
                audio_path = None
        
        if audio_path is None or not audio_path.exists():
            default_audio = self.segment02_dir / "Final_Audio" / "EXO_VOICE_FINAL.mp3"
            if default_audio.exists():
                audio_path = default_audio
            else:
                voice_samples = list((self.segment02_dir / "Voice_Samples").glob("*.mp3"))
                voice_samples.extend(list((self.segment02_dir / "Voice_Samples").glob("*.wav")))
                if voice_samples:
                    audio_path = voice_samples[0]
        
        if not audio_path or not audio_path.exists():
            print("[WARNING] Aucun fichier audio trouvé. Post-prod sans audio.")
            return rendered_video_path
        
        # Chemin du logo (sera créé si nécessaire)
        logo_path = self.ASSETS_DIR / "blox_render_logo.png"
        
        # Chemin de sortie final (nom unique par variante)
        output_filename = f"EXO_MISSION_{variant_id:03d}.mp4"
        output_path = self.OUTPUT_DIR / output_filename
        
        # Générer un seed unique pour cette variante (basé sur variant_id + timestamp)
        # Pour avoir un noise différent à chaque fois, mais déterministe par variante
        random.seed(variant_id * 137)  # Seed déterministe par variante
        noise_strength = random.uniform(0.4, 0.6)  # 0.4% à 0.6% (proche de 0.5%)
        
        # Décalage audio : 0.01s (variant_id détermine le sens)
        audio_delay = 0.01 if variant_id % 2 == 0 else -0.01
        
        print(f"[INFO] Noise : {noise_strength:.3f}%")
        print(f"[INFO] Décalage audio : {audio_delay:.3f}s")
        
        # Commande FFmpeg pour post-production
        # Tâche A + B + C : Fusion image+audio, logo (si présent), noise, décalage audio
        cmd = [
            "ffmpeg",
            "-i", str(rendered_video_path.resolve()),  # Vidéo Blender
            "-i", str(audio_path.resolve()),  # Audio source
            "-filter_complex",
            f"[0:v]noise=alls={noise_strength:.3f}:allf=t+u[v_noised]",  # Tâche C : Noise
            "-map", "[v_noised]",
            "-map", "1:a",  # Audio
            "-af", f"adelay={int(audio_delay * 1000)}|{int(audio_delay * 1000)}",  # Tâche C : Décalage audio (ms)
            "-c:v", "libx264",  # Codec vidéo H.264
            "-c:a", "aac",  # Codec audio AAC
            "-preset", "slow",  # Compression lente = meilleure qualité
            "-crf", "18",  # CRF 18 = High Quality (perceptually lossless)
            "-movflags", "+faststart",  # Fast start pour streaming web
            "-y",  # Overwrite si existe
            str(output_path.resolve())
        ]
        
        # Tâche B : Logo (si fichier présent, ajouter overlay)
        if logo_path.exists():
            print(f"[INFO] Logo trouvé : {logo_path.name}")
            # Commande FFmpeg avec logo overlay
            cmd_logo = [
                "ffmpeg",
                "-i", str(rendered_video_path.resolve()),
                "-i", str(audio_path.resolve()),
                "-i", str(logo_path.resolve()),
                "-filter_complex",
                f"[0:v]noise=alls={noise_strength:.3f}:allf=t+u[v_noised];"
                f"[v_noised][2:v]overlay=W-w-20:20[v_logo]",  # Logo en haut à droite
                "-map", "[v_logo]",
                "-map", "1:a",
                "-af", f"adelay={int(audio_delay * 1000)}|{int(audio_delay * 1000)}",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "slow",
                "-crf", "18",
                "-movflags", "+faststart",
                "-y",
                str(output_path.resolve())
            ]
            cmd = cmd_logo
        
        print(f"[INFO] Exécution FFmpeg : {' '.join(cmd[:10])}...")  # Afficher les premiers arguments
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max
            )
            
            if result.returncode != 0:
                print(f"[ERROR] FFmpeg a échoué : {result.stderr}")
                return rendered_video_path  # Retourner l'original si échec
            
            # Vérifier que le fichier final existe
            if output_path.exists():
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                
                # Calculer le hash MD5 du fichier (pour vérifier unicité YouTube)
                md5_hash = hashlib.md5()
                with open(output_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        md5_hash.update(chunk)
                file_hash = md5_hash.hexdigest()
                
                print(f"[SUCCESS] Post-prod terminée : {output_path.name}")
                print(f"[INFO] Taille : {file_size_mb:.2f} MB")
                print(f"[INFO] Hash MD5 : {file_hash[:16]}... (unique pour YouTube)")
                
                return output_path
            else:
                print(f"[ERROR] Fichier final non trouvé : {output_path}")
                return rendered_video_path
                
        except subprocess.TimeoutExpired:
            print("[ERROR] FFmpeg timeout (dépasse 10 minutes)")
            return rendered_video_path
        except Exception as e:
            print(f"[ERROR] Erreur lors de la post-prod : {e}")
            import traceback
            traceback.print_exc()
            return rendered_video_path

    def run(self, num_variantes: int = 1):
        """
        Exécute le pipeline complet de la Forge
        
        BOUCLE MAÎTRESSE : Exécute N fois le rendu avec des paramètres de "camouflage" différents.
        
        Args:
            num_variantes: Nombre de variantes à générer (Doctrine Asymétrie)
        """
        print("=" * 60)
        print("EXO_03_BLENDER_WORKER - Segment 03 : LEGION FORGE")
        print(f"VARIANTES DEMANDÉES : {num_variantes}")
        print("=" * 60)
        
        # Vérification des données d'entrée
        if not self.mission_ready_path.exists():
            print(f"[ERROR] Fichier mission introuvable : {self.mission_ready_path}")
            return False
        
        # SETUP UNIQUE (fait une seule fois)
        self.setup_scene()
        self.import_assets()
        self.setup_camera()
        self.setup_lighting()
        self.load_mission_data()  # Charger les données avant animation
        
        # BOUCLE MAÎTRESSE : Pour chaque variante
        for variant_id in range(num_variantes):
            print("=" * 60)
            print(f"VARIANTE {variant_id + 1}/{num_variantes}")
            print("=" * 60)
            
            # Pipeline de forge pour cette variante
            self.apply_animation()  # Animation pose (identique pour toutes variantes)
            self.apply_lip_sync()  # Lip-sync (identique pour toutes variantes)
            self.apply_camera_animation(variant_id=variant_id)  # Caméra (varie par variante)
            
            # Rendu vidéo
            rendered_path = self.render_video(variant_id=variant_id)
            
            # Post-production (fusion, logo, noise, décalage audio)
            final_path = self.post_prod_ghost(rendered_path, variant_id=variant_id)
            
            print(f"[SUCCESS] Variante {variant_id + 1}/{num_variantes} terminée : {final_path.name}")
        
        print("=" * 60)
        print(f"[SUCCESS] Pipeline Forge terminé avec succès ! ({num_variantes} variantes générées)")
        print("=" * 60)
        
        return True


def input_empereur():
    """
    INITIALISATION DE LA VARIANTE (INPUT EMPEREUR)
    
    Le script demande le nombre de variantes N souhaitées.
    """
    print("=" * 60)
    print("INPUT EMPEREUR - DOCTRINE ASYMÉTRIE")
    print("=" * 60)
    
    # Dans un environnement headless (Blender --background), on utilise sys.argv
    # Sinon, on pourrait utiliser input(), mais Blender headless ne supporte pas input()
    num_variantes = 1  # Par défaut
    
    # Essayer de lire depuis sys.argv (argument --num-variantes)
    if '--' in sys.argv:
        args_after_separator = sys.argv[sys.argv.index('--') + 1:]
        if '--num-variantes' in args_after_separator:
            idx = args_after_separator.index('--num-variantes')
            if idx + 1 < len(args_after_separator):
                try:
                    num_variantes = int(args_after_separator[idx + 1])
                except ValueError:
                    print("[WARNING] Argument --num-variantes invalide, utilisation de 1 par défaut")
    
    print(f"[INFO] Nombre de variantes : {num_variantes}")
    print("=" * 60)
    
    return num_variantes


def main():
    """
    Point d'entrée principal
    
    Note : Blender exécute ce script avec ses propres arguments.
    Les arguments utilisateur doivent être passés après le séparateur --.
    Exemple : blender --background --python EXO_03_BLENDER_WORKER.py -- --drive-root /path/to/root --num-variantes 3
    """
    # INPUT EMPEREUR : Demander le nombre de variantes
    num_variantes = input_empereur()
    
    # Initialisation de la Forge (parse automatiquement sys.argv après --)
    forge = EXOForge(drive_root=None)
    
    # Exécution du pipeline avec N variantes
    success = forge.run(num_variantes=num_variantes)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # Logique de lancement
    print("EXO_FORGE: Initialisation...")
    
    # Blender exécute ce script via: blender --background --python EXO_03_BLENDER_WORKER.py
    # Le main() sera appelé automatiquement
    main()

