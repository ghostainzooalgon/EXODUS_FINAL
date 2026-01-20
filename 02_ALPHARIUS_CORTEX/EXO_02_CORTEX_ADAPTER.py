#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXO_02_CORTEX_ADAPTER.py - Segment 02 : ALPHARIUS CORTEX
Système EXODUS - Adaptation et compilation des données pour mission finale

MODULES :
- AUTO-DEPLOY : Téléchargement automatique de Rhubarb Lip-Sync
- BRAIN ROT : Transformation du script en Slang US 2026 viral
- AUDIO GHOST : Normalisation audio
- PONT RHUBARB : Génération des formes de bouches (lip-sync)
- COMPILATION : Fusion des données Seg 01 + Seg 02
"""

import json
import os
import sys
import platform
import subprocess
import zipfile
import urllib.request
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


class EXOCortexAdapter:
    """
    Adaptateur Cortex pour transformation et compilation des données EXODUS
    """
    
    # URLs Rhubarb Lip-Sync (GitHub releases)
    RHUBARB_VERSION = "1.13.0"
    RHUBARB_WINDOWS_URL = f"https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v{RHUBARB_VERSION}/rhubarb-lip-sync-{RHUBARB_VERSION}-windows.zip"
    RHUBARB_LINUX_URL = f"https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v{RHUBARB_VERSION}/rhubarb-lip-sync-{RHUBARB_VERSION}-linux.zip"
    
    # Dictionnaire Brain Rot US 2026 (remplacement agressif 100%)
    BRAIN_ROT_DICT = {
        'Good': 'Sigma',
        'good': 'sigma',
        'GOOD': 'SIGMA',
        'Amazing': 'Rizzler',
        'amazing': 'rizzler',
        'AMAZING': 'RIZZLER',
        'Scary': 'Cooked',
        'scary': 'cooked',
        'SCARY': 'COOKED',
        'Fail': 'L',
        'fail': 'L',
        'FAIL': 'L',
        'Win': 'W',
        'win': 'W',
        'WIN': 'W',
        'Crazy': 'Ohio',
        'crazy': 'ohio',
        'CRAZY': 'OHIO',
    }
    
    def __init__(self, drive_root: Optional[str] = None):
        """
        Initialise l'adaptateur Cortex
        
        DOCTRINE DE L'ANCRE UNIQUE :
        - Tous les chemins sont basés sur drive_root
        - INPUT_DIR = drive_root / "00_INPUT" (vidéos sources)
        - DATA_DIR = drive_root / "01_BUFFER" (lecture et écriture JSON)
        - ASSETS_DIR = drive_root / "02_ASSETS" (assets audio si nécessaire)
        
        Args:
            drive_root: Racine du système de fichiers (ancre unique)
        """
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
        self.INPUT_DIR = self.drive_root / "00_INPUT"
        self.DATA_DIR = self.drive_root / "01_BUFFER"
        self.ASSETS_DIR = self.drive_root / "02_ASSETS"
        
        # Création des dossiers si nécessaire
        self.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Chemins spécifiques (compatibilité avec le reste du code)
        # Voice_Samples peut être dans DATA_DIR ou ASSETS_DIR selon préférence
        # On garde DATA_DIR pour cohérence avec la structure
        self.voice_samples_dir = self.DATA_DIR / "Voice_Samples"
        self.final_audio_dir = self.DATA_DIR / "Final_Audio"
        self.tools_dir = self.drive_root / "04_TOOLS"
        
        # Création des sous-dossiers si nécessaire
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.voice_samples_dir.mkdir(parents=True, exist_ok=True)
        self.final_audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Détection OS
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        
        # Chemin Rhubarb
        if self.is_windows:
            self.rhubarb_exe = self.tools_dir / "rhubarb-lip-sync.exe"
        else:
            self.rhubarb_exe = self.tools_dir / "rhubarb-lip-sync"
        
        # Racine Rhubarb (pour res/ et autres assets)
        self.rhubarb_root_dir = self.tools_dir
        
        # AFFICHAGE DES CHEMINS DÉTECTÉS (pour débuggage)
        print("=" * 80)
        print("[DOCTRINE DE L'ANCRE UNIQUE] - Segment 02 - Chemins détectés :")
        print("=" * 80)
        print(f"  RACINE (ANCRE)     : {self.drive_root}")
        print(f"  INPUT_DIR          : {self.INPUT_DIR}")
        print(f"  DATA_DIR            : {self.DATA_DIR}")
        print(f"  ASSETS_DIR          : {self.ASSETS_DIR}")
        print(f"  Voice Samples       : {self.voice_samples_dir}")
        print(f"  Final Audio         : {self.final_audio_dir}")
        print("=" * 80)

    def detect_mode(self, force_no_audio: bool = False) -> Tuple[str, Optional[Path]]:
        """
        SÉLECTEUR DE FLUX : Détecte le mode SILENT / DRAMA

        - DRAMA : un .mp3 est présent dans Voice_Samples/ ET pas de forçage no-audio
        - SILENT : aucun .mp3 trouvé OU forçage no-audio

        Returns:
            (mode, audio_file) où mode ∈ {"DRAMA", "SILENT"}
        """
        if force_no_audio:
            return ("SILENT", None)

        # DRAMA munitions : mp3 ou wav
        audio_files: List[Path] = []
        audio_files.extend(self.voice_samples_dir.glob("*.mp3"))
        audio_files.extend(self.voice_samples_dir.glob("*.wav"))
        audio_files = sorted(audio_files, key=lambda p: p.name.lower())

        if audio_files:
            return ("DRAMA", audio_files[0])

        return ("SILENT", None)

    def empty_speech_payload(self) -> Dict:
        """Payload speech minimal en mode SILENT."""
        return {
            "original_text": "",
            "viral_text": "",
            "transformation_applied": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "SILENT",
        }
    
    def setup_rhubarb(self) -> bool:
        """
        MODULE AUTO-DEPLOY
        Télécharge et configure Rhubarb Lip-Sync automatiquement
        
        Returns:
            True si succès, False sinon
        """
        print("[INFO] Vérification de Rhubarb Lip-Sync...")
        
        # Vérifier si déjà présent (chemin attendu)
        if self.rhubarb_exe.exists():
            print(f"[OK] Rhubarb trouvé : {self.rhubarb_exe}")
            return True
        
        # Vérifier si Rhubarb a déjà été extrait dans un sous-dossier (structure release GitHub)
        existing = None
        if self.is_windows:
            # typiquement: tools/Rhubarb-Lip-Sync-<ver>-Windows/rhubarb.exe
            candidates = list(self.tools_dir.glob("**/rhubarb.exe"))
        else:
            candidates = list(self.tools_dir.glob("**/rhubarb"))
        
        # Éviter les binaires annexes potentiels ; prendre le premier candidat plausible
        if candidates:
            existing = candidates[0]
        
        if existing and existing.exists():
            try:
                # Si le binaire vit dans un dossier de release, on utilise ce dossier comme racine (res/ à côté)
                self.rhubarb_root_dir = existing.parent
                shutil.copy2(existing, self.rhubarb_exe)
                # S'assurer que le dossier res/ est disponible sous tools/ pour PocketSphinx
                release_res = self.rhubarb_root_dir / "res"
                target_res = self.tools_dir / "res"
                if release_res.exists() and not target_res.exists():
                    shutil.copytree(release_res, target_res)
                if self.is_linux:
                    os.chmod(self.rhubarb_exe, 0o755)
                print(f"[OK] Rhubarb trouvé dans sous-dossier et copié : {self.rhubarb_exe}")
                return True
            except Exception as e:
                print(f"[WARNING] Rhubarb trouvé mais impossible à copier: {e}")
        
        print("[INFO] Rhubarb introuvable. Téléchargement automatique...")
        
        try:
            # Sélectionner l'URL selon l'OS
            if self.is_windows:
                url = self.RHUBARB_WINDOWS_URL
                zip_name = f"rhubarb-windows-{self.RHUBARB_VERSION}.zip"
            elif self.is_linux:
                url = self.RHUBARB_LINUX_URL
                zip_name = f"rhubarb-linux-{self.RHUBARB_VERSION}.zip"
            else:
                print(f"[ERROR] OS non supporté : {platform.system()}")
                return False
            
            zip_path = self.tools_dir / zip_name
            
            # Téléchargement
            print(f"[INFO] Téléchargement depuis GitHub...")
            urllib.request.urlretrieve(url, zip_path)
            print(f"[OK] Téléchargé : {zip_path}")
            
            # Extraction
            print(f"[INFO] Extraction...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.tools_dir)
            
            # Nettoyage
            zip_path.unlink()
            
            # Après extraction, la release contient souvent un sous-dossier.
            # On localise le binaire et on le copie vers le chemin attendu (tools/rhubarb-lip-sync[.exe]).
            extracted_bin = None
            if self.is_windows:
                extracted_candidates = list(self.tools_dir.glob("**/rhubarb.exe"))
            else:
                extracted_candidates = list(self.tools_dir.glob("**/rhubarb"))
            
            if extracted_candidates:
                extracted_bin = extracted_candidates[0]
            
            if extracted_bin and extracted_bin.exists():
                self.rhubarb_root_dir = extracted_bin.parent
                shutil.copy2(extracted_bin, self.rhubarb_exe)
                # Copier également res/ à côté de tools/ si nécessaire
                release_res = self.rhubarb_root_dir / "res"
                target_res = self.tools_dir / "res"
                if release_res.exists() and not target_res.exists():
                    shutil.copytree(release_res, target_res)
                if self.is_linux:
                    os.chmod(self.rhubarb_exe, 0o755)
                    print(f"[OK] Permissions d'exécution appliquées")
                print(f"[OK] Rhubarb binaire copié : {self.rhubarb_exe}")
            
            # Vérification finale
            if self.rhubarb_exe.exists():
                print(f"[SUCCESS] Rhubarb installé : {self.rhubarb_exe}")
                return True
            else:
                print(f"[ERROR] Rhubarb non trouvé après installation")
                return False
                
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'installation de Rhubarb : {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def transfigure_script(self, raw_data_path: Path) -> Dict:
        """
        MODULE BRAIN ROT
        Transforme la transcription en Slang US 2026 viral
        
        Args:
            raw_data_path: Chemin vers mission_RAW.json
            
        Returns:
            Dict contenant le script transformé
        """
        print("[INFO] Module Brain Rot : Transformation du script...")
        
        try:
            with open(raw_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire la transcription (première frame avec audio)
            original_text = ""
            for frame in data.get('frames', []):
                audio = frame.get('audio_transcription')
                if audio and audio.get('text'):
                    original_text = audio.get('text', '')
                    break
            
            if not original_text:
                print("[WARNING] Aucune transcription trouvée dans les données")
                original_text = ""
            
            # Transformation Brain Rot (remplacement agressif 100%)
            viral_text = original_text
            for old_word, new_word in self.BRAIN_ROT_DICT.items():
                viral_text = viral_text.replace(old_word, new_word)
            
            print(f"[OK] Script transformé : {len(viral_text)} caractères")
            print(f"[INFO] Original : {original_text[:100]}...")
            print(f"[INFO] Viral : {viral_text[:100]}...")
            
            return {
                "original_text": original_text,
                "viral_text": viral_text,
                "transformation_applied": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de la transformation : {e}")
            import traceback
            traceback.print_exc()
            return {
                "original_text": "",
                "viral_text": "",
                "transformation_applied": False,
                "error": str(e)
            }
    
    def normalize_audio(self, input_file: Optional[Path] = None) -> Optional[Path]:
        """
        MODULE AUDIO GHOST
        Normalise l'audio depuis Voice_Samples/
        
        Returns:
            Chemin vers EXO_VOICE_FINAL.mp3 ou None
        """
        print("[INFO] Module Audio Ghost : Normalisation audio...")
        
        try:
            from pydub import AudioSegment
            from pydub.effects import normalize
            
            if input_file is None:
                # fallback legacy : premier mp3
                mp3_files = list(self.voice_samples_dir.glob("*.mp3"))
                if not mp3_files:
                    print("[WARNING] Aucun fichier .mp3 trouvé dans Voice_Samples/")
                    return None
                input_file = mp3_files[0]
            print(f"[INFO] Fichier trouvé : {input_file.name}")
            
            # Charger l'audio
            audio = AudioSegment.from_mp3(str(input_file))
            print(f"[INFO] Audio chargé : {len(audio)}ms, {audio.frame_rate}Hz")
            
            # Normalisation du volume
            audio = normalize(audio)
            print("[OK] Volume normalisé")
            
            # Réduction de bruit basique (compression dynamique)
            audio = audio.compress_dynamic_range(threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
            print("[OK] Compression appliquée")
            
            # Sauvegarde
            output_path = self.final_audio_dir / "EXO_VOICE_FINAL.mp3"
            audio.export(str(output_path), format="mp3", bitrate="192k")
            print(f"[SUCCESS] Audio normalisé sauvegardé : {output_path}")
            
            return output_path
            
        except ImportError:
            print("[ERROR] pydub non installé. Installez avec: pip install pydub")
            return None
        except Exception as e:
            print(f"[ERROR] Erreur lors de la normalisation : {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_lip_sync(self, audio_path: Path) -> Optional[Dict]:
        """
        PONT RHUBARB
        Génère les données de lip-sync via Rhubarb
        
        Args:
            audio_path: Chemin vers EXO_VOICE_FINAL.mp3
            
        Returns:
            Dict contenant les données de lip-sync ou None
        """
        print("[INFO] Pont Rhubarb : Génération lip-sync...")
        
        if not self.rhubarb_exe.exists():
            print("[ERROR] Rhubarb non trouvé. Exécutez setup_rhubarb() d'abord.")
            return None
        
        if not audio_path.exists():
            print(f"[ERROR] Fichier audio introuvable : {audio_path}")
            return None
        
        try:
            output_json = self.final_audio_dir / "EXO_LIP_SYNC.json"
            
            # Commande Rhubarb
            cmd = [
                str(self.rhubarb_exe),
                "-f", "json",
                str(audio_path.resolve()),
                "-o", str(output_json.resolve())
            ]
            
            print(f"[INFO] Exécution : {' '.join(cmd)}")
            # IMPORTANT: Rhubarb dépend de res/ (PocketSphinx). On force le cwd sur la racine Rhubarb
            # pour éviter les erreurs du type tools\\res\\... introuvable.
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.rhubarb_root_dir),
                timeout=300  # 5 minutes max
            )
            
            if result.returncode != 0:
                print(f"[ERROR] Rhubarb a échoué : {result.stderr}")
                return None
            
            # Lire le résultat
            if output_json.exists():
                with open(output_json, 'r', encoding='utf-8') as f:
                    lip_sync_data = json.load(f)
                print(f"[SUCCESS] Lip-sync généré : {len(lip_sync_data.get('mouthCues', []))} formes")
                return lip_sync_data
            else:
                print("[ERROR] Fichier de sortie non généré")
                return None
                
        except subprocess.TimeoutExpired:
            print("[ERROR] Rhubarb timeout (dépasse 5 minutes)")
            return None
        except Exception as e:
            print(f"[ERROR] Erreur lors de la génération lip-sync : {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def compile_mission(
        self,
        raw_data_path: Path,
        speech_data: Dict,
        lip_sync_data: Optional[Dict],
        mode: str,
    ) -> Path:
        """
        COMPILATION
        Fusionne toutes les données en EXO_MISSION_READY.json
        
        Args:
            raw_data_path: Chemin vers mission_RAW.json (Segment 01)
            speech_data: Données du script transformé
            lip_sync_data: Données de lip-sync (optionnel)
            
        Returns:
            Chemin vers EXO_MISSION_READY.json
        """
        print("[INFO] Compilation : Fusion des données...")
        
        try:
            # Charger les données du Segment 01 (SCANNER UNIVERSEL)
            with open(raw_data_path, 'r', encoding='utf-8') as f:
                seg01_data = json.load(f)
            
            # PASS-THROUGH : on récupère directement les blocs universels
            metadata_raw = seg01_data.get("metadata", {})
            camera_motion = seg01_data.get("camera_motion", [])
            actors_block = seg01_data.get("actors", {})
            
            # Préparer speech (Script + Timestamps)
            speech_output = {
                "original_text": speech_data.get('original_text', ''),
                "viral_text": speech_data.get('viral_text', ''),
                "transformation_applied": speech_data.get('transformation_applied', False),
                "timestamp": speech_data.get('timestamp', datetime.now(timezone.utc).isoformat())
            }
            
            # Préparer mouth (Lip-sync)
            if mode == "SILENT":
                mouth_output = {
                    "mouthCues": [],
                    "metadata": {
                        "status": "silent_default",
                        "mode": "SILENT",
                        "default_mouth_open_ratio": 0.0
                    }
                }
            else:
                # MODE DRAMA : priorité au fichier EXO_LIP_SYNC.json sur disque
                lip_sync_path = self.final_audio_dir / "EXO_LIP_SYNC.json"
                lip_sync_payload = None
                if lip_sync_path.exists():
                    try:
                        with open(lip_sync_path, 'r', encoding='utf-8') as f:
                            lip_sync_payload = json.load(f)
                    except Exception:
                        lip_sync_payload = None

                if lip_sync_payload:
                    mouth_output = {
                        "mouthCues": lip_sync_payload.get("mouthCues", []),
                        "metadata": lip_sync_payload.get("metadata", {})
                    }
                elif lip_sync_data:
                    mouth_output = {
                        "mouthCues": lip_sync_data.get('mouthCues', []),
                        "metadata": lip_sync_data.get('metadata', {})
                    }
                else:
                    mouth_output = {
                        "mouthCues": [],
                        "metadata": {"status": "not_generated", "mode": mode}
                    }
            
            # Compiler le fichier final (PROTOCOLE BABEL)
            mission_data = {
                "metadata": {
                    "mission_id": f"EXO_MISSION_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                    "language": "en-US",
                    "os_detected": platform.system(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source_segment01": str(raw_data_path),
                    "mode": mode,
                    "source_metadata": metadata_raw,
                },
                # Pass-through géométrie brute
                "camera_motion": camera_motion,
                "actors": actors_block,
                # Bloc audio / texte
                "speech": speech_output,
                "mouth": mouth_output,
                # Clé de synchronisation globale pour la Forge
                "global_audio_sync": {
                    "primary_actor_id": "0",
                    "lip_sync_status": mouth_output.get("metadata", {}).get("status", "silent_default"),
                },
            }
            
            # Sauvegarde dans DATA_DIR (01_BUFFER)
            output_path = self.DATA_DIR / "EXO_MISSION_READY.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(mission_data, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] Mission compilée : {output_path}")
            print(f"[INFO] Acteurs : {len(actors_block.keys())}")
            print(f"[INFO] Frames camera_motion : {len(camera_motion)}")
            print(f"[INFO] Formes de bouches : {len(mouth_output.get('mouthCues', []))}")
            
            return output_path
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de la compilation : {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def run(self):
        """
        Exécute le pipeline complet
        """
        print("=" * 60)
        print("EXO_02_CORTEX_ADAPTER - Segment 02 : ALPHARIUS CORTEX")
        print("=" * 60)
        
        # 1. Charger les données Segment 01 (SCANNER UNIVERSEL - mission_RAW.json)
        raw_data_path = self.DATA_DIR / "mission_RAW.json"
        if not raw_data_path.exists():
            print(f"[ERROR] Fichier Segment 01 introuvable : {raw_data_path}")
            print(f"[INFO] Assurez-vous que le Segment 01 a été exécuté et a généré mission_RAW.json dans {self.DATA_DIR}")
            return False

        # 2. SÉLECTEUR DE FLUX (Silent / Drama)
        mode, audio_input = self.detect_mode(getattr(self, "_force_no_audio", False))
        if mode == "SILENT":
            print("[INFO] : MODE SILENT DÉTECTÉ - SAUT DU LIP-SYNC.")
        else:
            print(f"[INFO] : MODE DRAMA DÉTECTÉ - Audio: {audio_input.name if audio_input else 'N/A'}")

        # 3. Pipeline conditionnel
        speech_data = self.empty_speech_payload()
        lip_sync_data = None

        if mode == "DRAMA":
            # AUTO-DEPLOY uniquement si DRAMA (gain de temps en SILENT)
            if not self.setup_rhubarb():
                print("[ERROR] Échec du setup Rhubarb. Abandon.")
                return False

            # Brain Rot en DRAMA
            speech_data = self.transfigure_script(raw_data_path)

            # Audio Ghost + Rhubarb
            audio_path: Optional[Path] = None
            if audio_input and audio_input.suffix.lower() == ".wav":
                # WAV: Rhubarb peut consommer directement, pas besoin de pydub.
                audio_path = audio_input
                print("[INFO] Audio WAV détecté : saut de la normalisation, envoi direct à Rhubarb")
            else:
                audio_path = self.normalize_audio(audio_input)

            if audio_path:
                lip_sync_data = self.generate_lip_sync(audio_path)
            else:
                print("[WARNING] Pas d'audio, lip-sync ignoré")

        # 4. COMPILATION UNIVERSELLE
        mission_path = self.compile_mission(raw_data_path, speech_data, lip_sync_data, mode)
        
        print("=" * 60)
        print("[SUCCESS] Pipeline Cortex terminé avec succès !")
        print(f"[OK] Fichier final : {mission_path}")
        print("=" * 60)
        
        return True


def main():
    """
    Point d'entrée principal
    
    DOCTRINE DE L'ANCRE UNIQUE :
    - Accepte --drive-root (obligatoire)
    - Tous les chemins sont basés sur drive_root
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="EXO Cortex Adapter - Segment 02")
    parser.add_argument(
        "--drive-root",
        type=str,
        default=None,
        help="Racine du système de fichiers (ancre unique). Défaut Colab: /content/drive/MyDrive/EXODUS_SYSTEM"
    )
    parser.add_argument("--no-audio", action="store_true", help="Force le MODE SILENT (ignore Voice_Samples/)")
    
    args = parser.parse_args()
    
    adapter = EXOCortexAdapter(args.drive_root)
    adapter._force_no_audio = bool(args.no_audio)
    success = adapter.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


