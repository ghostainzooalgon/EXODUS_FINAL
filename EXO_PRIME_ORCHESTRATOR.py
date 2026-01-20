#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXO_PRIME_ORCHESTRATOR.py - Système Nerveux Central EXODUS
Orchestrateur Suprême : Automatisation complète du pipeline SOURCING → INQUISITION → CORTEX → MANUFACTORUM

PROTOCOLE SINGULARITÉ :
- Surveillance automatique du dossier Raw_Videos/
- Pipeline automatisé pour chaque vidéo source
- Gestion des erreurs et résilience
- Interface de commandement impériale
"""

import subprocess
import sys
import time
import argparse
import ast
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import json
import shutil
from datetime import datetime
import platform


class EXOPrimeOrchestrator:
    """
    Orchestrateur Suprême EXODUS
    Système nerveux central qui coordonne les Segments 01, 02, 03
    """
    
    def __init__(self):
        """Initialise l'Orchestrateur"""
        # Détection automatique de la racine du projet
        self.project_root = Path(__file__).parent.resolve()
        
        # Chemins des segments
        self.segment01_dir = self.project_root / "01_EYE_INQUISITION"
        self.segment02_dir = self.project_root / "02_ALPHARIUS_CORTEX"
        self.segment03_dir = self.project_root / "03_LEGION_FORGE"
        
        # Dossiers de surveillance et de travail
        self.raw_videos_dir = self.segment01_dir / "Raw_Videos"
        self.extraction_data_dir = self.segment01_dir / "Extraction_Data"
        self.final_audio_dir = self.segment02_dir / "Final_Audio"
        self.voice_samples_dir = self.segment02_dir / "Voice_Samples"
        self.exports_dir = self.segment03_dir / "Exports_4K"
        
        # Scripts des segments
        self.dna_scanner = self.segment01_dir / "EXO_01_DNA_SCANNER.py"
        self.cortex_adapter = self.segment02_dir / "EXO_02_CORTEX_ADAPTER.py"
        self.blender_worker = self.segment03_dir / "EXO_03_BLENDER_WORKER.py"
        
        # Création des dossiers si nécessaire
        self.raw_videos_dir.mkdir(parents=True, exist_ok=True)
        self.extraction_data_dir.mkdir(parents=True, exist_ok=True)
        self.final_audio_dir.mkdir(parents=True, exist_ok=True)
        self.voice_samples_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistiques de l'Empire
        self.stats = {
            "total_videos": 0,
            "processed": 0,
            "failed": 0,
            "variants_generated": 0,
            "start_time": None,
            "errors": []
        }
        
        print(f"[INFO] Orchestrateur initialisé - Racine: {self.project_root}")
    
    def dry_run_diagnostic(self) -> Dict[str, bool]:
        """
        PROTOCOLE DRY-RUN : Diagnostic complet sans exécution
        
        Vérifie :
        - Assets (avatar.glb, map_brookhaven.glb, blox_render_logo.png)
        - Environnement (ffmpeg, blender)
        - Permissions d'écriture (fichiers .tmp)
        - Syntaxe des scripts Python
        
        Returns:
            Dict avec résultats de chaque vérification
        """
        print("=" * 80)
        print("PROTOCOLE DRY-RUN - DIAGNOSTIC COMPLET")
        print("=" * 80)
        
        results = {
            "assets": {},
            "environment": {},
            "permissions": {},
            "syntax": {}
        }
        
        # 1. VÉRIFICATION ASSETS
        print("\n[DIAGNOSTIC] Vérification des Assets...")
        assets_dir = self.segment03_dir / "Imperial_Assets"
        
        required_assets = {
            "avatar.glb": assets_dir / "avatar.glb",
            "map_brookhaven.glb": assets_dir / "map_brookhaven.glb",
            "blox_render_logo.png": assets_dir / "blox_render_logo.png"
        }
        
        all_assets_ok = True
        for asset_name, asset_path in required_assets.items():
            exists = asset_path.exists()
            results["assets"][asset_name] = exists
            status = "[OK]" if exists else "[MISSING]"
            print(f"  {status} {asset_name}: {'Trouve' if exists else 'MANQUANT'}")
            if not exists:
                all_assets_ok = False
                print(f"      Chemin attendu : {asset_path}")
        
        results["assets"]["all_ok"] = all_assets_ok
        
        # 2. VÉRIFICATION ENVIRONNEMENT
        print("\n[DIAGNOSTIC] Vérification de l'Environnement...")
        
        # FFmpeg
        ffmpeg_found = False
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            ffmpeg_found = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            ffmpeg_found = False
        
        results["environment"]["ffmpeg"] = ffmpeg_found
        status = "[OK]" if ffmpeg_found else "[MISSING]"
        print(f"  {status} FFmpeg: {'Trouve' if ffmpeg_found else 'MANQUANT'}")
        if ffmpeg_found:
            version_line = result.stdout.split('\n')[0] if ffmpeg_found else ""
            print(f"      {version_line[:60]}")
        
        # Blender
        blender_exe = self._find_blender()
        blender_found = blender_exe is not None
        results["environment"]["blender"] = blender_found
        status = "[OK]" if blender_found else "[MISSING]"
        print(f"  {status} Blender: {'Trouve' if blender_found else 'MANQUANT'}")
        if blender_found:
            print(f"      Chemin : {blender_exe}")
        
        results["environment"]["all_ok"] = ffmpeg_found and blender_found
        
        # 3. VÉRIFICATION PERMISSIONS D'ÉCRITURE
        print("\n[DIAGNOSTIC] Vérification des Permissions d'Écriture...")
        
        test_dirs = {
            "Extraction_Data": self.extraction_data_dir,
            "Final_Audio": self.final_audio_dir,
            "Exports_4K": self.exports_dir
        }
        
        all_permissions_ok = True
        for dir_name, dir_path in test_dirs.items():
            try:
                # Créer le dossier si nécessaire
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Tester l'écriture avec un fichier .tmp
                test_file = dir_path / f"EXO_TEST_WRITE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp"
                test_file.write_text("EXODUS_TEST")
                
                # Vérifier la lecture
                if test_file.read_text() == "EXODUS_TEST":
                    # Nettoyer
                    test_file.unlink()
                    results["permissions"][dir_name] = True
                    print(f"  [OK] {dir_name}: Permissions OK")
                else:
                    results["permissions"][dir_name] = False
                    all_permissions_ok = False
                    print(f"  [FAIL] {dir_name}: Echec de lecture")
            except Exception as e:
                results["permissions"][dir_name] = False
                all_permissions_ok = False
                print(f"  [FAIL] {dir_name}: Erreur - {str(e)[:50]}")
        
        results["permissions"]["all_ok"] = all_permissions_ok
        
        # 4. VÉRIFICATION SYNTAXE DES SCRIPTS PYTHON
        print("\n[DIAGNOSTIC] Vérification de la Syntaxe des Scripts...")
        
        python_scripts = {
            "EXO_01_DNA_SCANNER.py": self.dna_scanner,
            "EXO_02_CORTEX_ADAPTER.py": self.cortex_adapter,
            "EXO_03_BLENDER_WORKER.py": self.blender_worker,
            "EXO_PRIME_ORCHESTRATOR.py": self.project_root / "EXO_PRIME_ORCHESTRATOR.py"
        }
        
        all_syntax_ok = True
        for script_name, script_path in python_scripts.items():
            if not script_path.exists():
                results["syntax"][script_name] = False
                all_syntax_ok = False
                print(f"  [FAIL] {script_name}: Fichier introuvable")
                continue
            
            try:
                # Lire et parser le fichier pour vérifier la syntaxe
                with open(script_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Parser avec ast pour vérifier la syntaxe
                ast.parse(source_code, filename=str(script_path))
                results["syntax"][script_name] = True
                print(f"  [OK] {script_name}: Syntaxe valide")
            except SyntaxError as e:
                results["syntax"][script_name] = False
                all_syntax_ok = False
                print(f"  [FAIL] {script_name}: Erreur de syntaxe ligne {e.lineno}")
                print(f"      {e.msg}")
            except Exception as e:
                results["syntax"][script_name] = False
                all_syntax_ok = False
                print(f"  [FAIL] {script_name}: Erreur - {str(e)[:50]}")
        
        results["syntax"]["all_ok"] = all_syntax_ok
        
        # RAPPORT FINAL
        print("\n" + "=" * 80)
        print("RAPPORT DE PRÊT À L'INFILTRATION")
        print("=" * 80)
        
        all_checks_passed = (
            results["assets"]["all_ok"] and
            results["environment"]["all_ok"] and
            results["permissions"]["all_ok"] and
            results["syntax"]["all_ok"]
        )
        
        if all_checks_passed:
            print("[SATELLITE SYNC] : Système EXODUS validé logiquement.")
            print("Prêt pour le push GitHub et le déploiement Cloud.")
            print("=" * 80)
        else:
            print("[WARNING] Certaines vérifications ont échoué :")
            if not results["assets"]["all_ok"]:
                print("  - Assets manquants")
            if not results["environment"]["all_ok"]:
                print("  - Outils système manquants (FFmpeg/Blender)")
            if not results["permissions"]["all_ok"]:
                print("  - Problèmes de permissions d'écriture")
            if not results["syntax"]["all_ok"]:
                print("  - Erreurs de syntaxe dans les scripts")
            print("=" * 80)
        
        return results
    
    def scan_raw_videos(self) -> List[Path]:
        """
        SCAN : Surveille le dossier Raw_Videos/ pour détecter les fichiers .mp4
        
        Returns:
            Liste des chemins vers les vidéos .mp4 trouvées
        """
        print(f"[INFO] Scan du dossier Raw_Videos/...")
        
        video_files = list(self.raw_videos_dir.glob("*.mp4"))
        video_files.extend(list(self.raw_videos_dir.glob("*.MP4")))
        
        # Trier par nom pour ordre prévisible
        video_files = sorted(video_files, key=lambda p: p.name.lower())
        
        print(f"[INFO] {len(video_files)} vidéo(s) détectée(s)")
        for i, video in enumerate(video_files, 1):
            print(f"  [{i}] {video.name}")
        
        return video_files
    
    def execute_segment01(self, video_path: Path) -> Optional[Path]:
        """
        SÉQUENCE DE DESTRUCTION - Segment 01 : INQUISITION
        
        Lance le DNA Scanner pour extraire l'ADN de la vidéo source.
        
        Args:
            video_path: Chemin vers la vidéo source
            
        Returns:
            Chemin vers EXO_DATA_RAW.json ou None si échec
        """
        print(f"[SEGMENT 01] Extraction ADN de {video_path.name}...")
        
        if not self.dna_scanner.exists():
            error_msg = f"[ERROR] Script Segment 01 introuvable : {self.dna_scanner}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return None
        
        # Chemin de sortie
        output_json = self.extraction_data_dir / "EXO_DATA_RAW.json"
        
        try:
            # Commande : python EXO_01_DNA_SCANNER.py <video> -o <output>
            cmd = [
                sys.executable,
                str(self.dna_scanner),
                str(video_path.resolve()),
                "-o", str(output_json.resolve())
            ]
            
            print(f"[INFO] Exécution : {' '.join(cmd[:3])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 heure max par vidéo
            )
            
            if result.returncode != 0:
                error_msg = f"[ERROR] Segment 01 échoué pour {video_path.name}: {result.stderr[:200]}"
                print(error_msg)
                self.stats["errors"].append(error_msg)
                return None
            
            # Vérifier que le fichier JSON a été créé
            if output_json.exists():
                print(f"[SUCCESS] Segment 01 terminé : {output_json.name}")
                return output_json
            else:
                error_msg = f"[ERROR] Fichier JSON non généré : {output_json}"
                print(error_msg)
                self.stats["errors"].append(error_msg)
                return None
                
        except subprocess.TimeoutExpired:
            error_msg = f"[ERROR] Segment 01 timeout pour {video_path.name}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return None
        except Exception as e:
            error_msg = f"[ERROR] Erreur Segment 01 pour {video_path.name}: {e}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            import traceback
            traceback.print_exc()
            return None
    
    def execute_segment02(self, mode: str) -> bool:
        """
        SÉQUENCE DE DESTRUCTION - Segment 02 : CORTEX
        
        Lance le Cortex Adapter pour transfigurer l'audio et le script.
        
        Args:
            mode: Mode global (DRAMA ou SILENT)
            
        Returns:
            True si succès, False sinon
        """
        print(f"[SEGMENT 02] Transformation Cortex (mode: {mode})...")
        
        if not self.cortex_adapter.exists():
            error_msg = f"[ERROR] Script Segment 02 introuvable : {self.cortex_adapter}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return False
        
        try:
            # Commande : python EXO_02_CORTEX_ADAPTER.py [--no-audio si SILENT]
            cmd = [
                sys.executable,
                str(self.cortex_adapter)
            ]
            
            if mode == "SILENT":
                cmd.append("--no-audio")
            
            print(f"[INFO] Exécution : {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes max
            )
            
            if result.returncode != 0:
                error_msg = f"[ERROR] Segment 02 échoué : {result.stderr[:200]}"
                print(error_msg)
                self.stats["errors"].append(error_msg)
                return False
            
            # Vérifier que EXO_MISSION_READY.json a été créé
            mission_ready = self.segment02_dir / "EXO_MISSION_READY.json"
            if mission_ready.exists():
                print(f"[SUCCESS] Segment 02 terminé : {mission_ready.name}")
                return True
            else:
                error_msg = f"[ERROR] Fichier mission non généré : {mission_ready}"
                print(error_msg)
                self.stats["errors"].append(error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "[ERROR] Segment 02 timeout"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return False
        except Exception as e:
            error_msg = f"[ERROR] Erreur Segment 02 : {e}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            import traceback
            traceback.print_exc()
            return False
    
    def execute_segment03(self, num_variantes: int) -> int:
        """
        SÉQUENCE DE DESTRUCTION - Segment 03 : MANUFACTORUM
        
        Lance le Manufactorum Blender pour générer N variantes.
        
        Args:
            num_variantes: Nombre de variantes à générer
            
        Returns:
            Nombre de variantes générées avec succès
        """
        print(f"[SEGMENT 03] Manufactorum Blender ({num_variantes} variante(s))...")
        
        if not self.blender_worker.exists():
            error_msg = f"[ERROR] Script Segment 03 introuvable : {self.blender_worker}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return 0
        
        # Détecter Blender (Windows vs Linux/Colab)
        blender_exe = self._find_blender()
        if not blender_exe:
            error_msg = "[ERROR] Blender non trouvé. Installez Blender ou configurez le chemin."
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return 0
        
        try:
            # Commande : blender --background --python EXO_03_BLENDER_WORKER.py -- --drive-root <root> --num-variantes <N>
            cmd = [
                str(blender_exe),
                "--background",
                "--python", str(self.blender_worker.resolve()),
                "--",
                "--drive-root", str(self.project_root.resolve()),
                "--num-variantes", str(num_variantes)
            ]
            
            print(f"[INFO] Exécution Blender : {blender_exe.name}...")
            print(f"[INFO] Variantes demandées : {num_variantes}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200 * num_variantes  # 2 heures par variante max
            )
            
            if result.returncode != 0:
                error_msg = f"[ERROR] Segment 03 échoué : {result.stderr[:500]}"
                print(error_msg)
                self.stats["errors"].append(error_msg)
                # Compter les fichiers générés malgré l'erreur
                return self._count_generated_variants()
            
            # Compter les fichiers générés
            variants_generated = self._count_generated_variants()
            print(f"[SUCCESS] Segment 03 terminé : {variants_generated} variante(s) générée(s)")
            return variants_generated
                
        except subprocess.TimeoutExpired:
            error_msg = f"[ERROR] Segment 03 timeout (dépasse {7200 * num_variantes}s)"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            return self._count_generated_variants()
        except Exception as e:
            error_msg = f"[ERROR] Erreur Segment 03 : {e}"
            print(error_msg)
            self.stats["errors"].append(error_msg)
            import traceback
            traceback.print_exc()
            return self._count_generated_variants()
    
    def _find_blender(self) -> Optional[Path]:
        """
        Trouve l'exécutable Blender sur le système
        
        Returns:
            Chemin vers blender.exe ou blender, ou None si non trouvé
        """
        # Windows
        if platform.system() == "Windows":
            # Chemins communs Windows
            common_paths = [
                Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender/blender.exe"),
            ]
            for path in common_paths:
                if path.exists():
                    return path
            
            # Essayer depuis PATH
            try:
                result = subprocess.run(["where", "blender"], capture_output=True, text=True)
                if result.returncode == 0:
                    blender_path = Path(result.stdout.strip().split('\n')[0])
                    if blender_path.exists():
                        return blender_path
            except:
                pass
        
        # Linux/Colab
        else:
            # Essayer depuis PATH
            try:
                result = subprocess.run(["which", "blender"], capture_output=True, text=True)
                if result.returncode == 0:
                    blender_path = Path(result.stdout.strip())
                    if blender_path.exists():
                        return blender_path
            except:
                pass
        
        return None
    
    def _count_generated_variants(self) -> int:
        """
        Compte les fichiers EXO_MISSION_*.mp4 générés dans Exports_4K/
        
        Returns:
            Nombre de fichiers trouvés
        """
        variants = list(self.exports_dir.glob("EXO_MISSION_*.mp4"))
        return len(variants)
    
    def process_video(self, video_path: Path, mode: str, num_variantes: int, video_index: int, total_videos: int) -> bool:
        """
        Traite une vidéo complète : S01 → S02 → S03
        
        Args:
            video_path: Chemin vers la vidéo source
            mode: Mode global (DRAMA ou SILENT)
            num_variantes: Nombre de variantes à générer
            video_index: Index de la vidéo (pour affichage)
            total_videos: Total de vidéos à traiter
            
        Returns:
            True si succès complet, False sinon
        """
        print("=" * 80)
        print(f"[VIDEO {video_index}/{total_videos}] {video_path.name}")
        print("=" * 80)
        
        # SEGMENT 01 : INQUISITION
        raw_data_path = self.execute_segment01(video_path)
        if raw_data_path is None:
            print(f"[FAILURE] Segment 01 échoué pour {video_path.name}. Passage à la vidéo suivante.")
            self.stats["failed"] += 1
            return False
        
        # SEGMENT 02 : CORTEX
        if not self.execute_segment02(mode):
            print(f"[FAILURE] Segment 02 échoué pour {video_path.name}. Passage à la vidéo suivante.")
            self.stats["failed"] += 1
            return False
        
        # SEGMENT 03 : MANUFACTORUM
        variants_before = self._count_generated_variants()
        variants_generated = self.execute_segment03(num_variantes)
        variants_after = self._count_generated_variants()
        
        if variants_generated == 0:
            print(f"[FAILURE] Segment 03 n'a généré aucune variante pour {video_path.name}.")
            self.stats["failed"] += 1
            return False
        
        # Mise à jour des statistiques
        self.stats["processed"] += 1
        self.stats["variants_generated"] += variants_generated
        
        print(f"[SUCCESS] Vidéo {video_index}/{total_videos} traitée avec succès ({variants_generated} variante(s))")
        print("=" * 80)
        
        return True
    
    def run(self, mode: str, num_variantes: int):
        """
        Exécute le pipeline complet de l'Orchestrateur
        
        Args:
            mode: Mode global (DRAMA ou SILENT)
            num_variantes: Nombre de variantes par vidéo source
        """
        print("=" * 80)
        print("EXO_PRIME_ORCHESTRATOR - SYSTÈME NERVEUX CENTRAL EXODUS")
        print("=" * 80)
        print(f"[INFO] Mode global : {mode}")
        print(f"[INFO] Variantes par source : {num_variantes}")
        print("=" * 80)
        
        self.stats["start_time"] = datetime.now()
        
        # SCAN : Détecter les vidéos
        video_files = self.scan_raw_videos()
        
        if not video_files:
            print("[WARNING] Aucune vidéo trouvée dans Raw_Videos/. L'Orchestrateur attend...")
            print("[INFO] Placez des fichiers .mp4 dans Raw_Videos/ pour démarrer le traitement.")
            return
        
        self.stats["total_videos"] = len(video_files)
        
        print("=" * 80)
        print(f"[INFO] Démarrage du traitement de {len(video_files)} vidéo(s)...")
        print("=" * 80)
        
        # TRAITEMENT : Pour chaque vidéo
        for idx, video_path in enumerate(video_files, 1):
            try:
                # Barre de progression de l'Empire
                print(f"\n[PROGRESS] Vidéo {idx}/{len(video_files)} - {video_path.name}")
                
                # Traitement complet
                success = self.process_video(video_path, mode, num_variantes, idx, len(video_files))
                
                if not success:
                    # RÉSILIENCE : Continuer même en cas d'échec
                    print(f"[RESILIENCE] Vidéo {idx} échouée, passage à la suivante...")
                    continue
                
            except Exception as e:
                # RÉSILIENCE : Logger l'erreur et continuer
                error_msg = f"[ERROR] Erreur fatale pour {video_path.name}: {e}"
                print(error_msg)
                self.stats["errors"].append(error_msg)
                self.stats["failed"] += 1
                import traceback
                traceback.print_exc()
                continue
        
        # RAPPORT FINAL DE L'EMPIRE
        self._print_final_report()
    
    def _print_final_report(self):
        """Affiche le rapport final de l'Empire"""
        print("\n" + "=" * 80)
        print("RAPPORT FINAL DE L'EMPIRE")
        print("=" * 80)
        
        end_time = datetime.now()
        duration = (end_time - self.stats["start_time"]).total_seconds() if self.stats["start_time"] else 0
        
        print(f"Vidéos totales : {self.stats['total_videos']}")
        print(f"Vidéos traitées : {self.stats['processed']}")
        print(f"Vidéos échouées : {self.stats['failed']}")
        print(f"Variantes générées : {self.stats['variants_generated']}")
        print(f"Durée totale : {duration / 60:.1f} minutes")
        
        if self.stats["errors"]:
            print(f"\nErreurs rencontrées : {len(self.stats['errors'])}")
            for i, error in enumerate(self.stats["errors"][:10], 1):  # Afficher les 10 premières
                print(f"  [{i}] {error[:100]}...")
            if len(self.stats["errors"]) > 10:
                print(f"  ... et {len(self.stats['errors']) - 10} autres erreurs")
        
        print("=" * 80)
        print("[SUCCESS] Orchestrateur terminé. L'Empire est satisfait.")
        print("=" * 80)


def interface_commandement() -> Tuple[str, int]:
    """
    INTERFACE DE COMMANDEMENT
    
    Demande à l'Empereur :
    - Mode global (DRAMA/SILENT)
    - Nombre de variantes par source
    
    Returns:
        (mode, num_variantes)
    """
    print("=" * 80)
    print("INTERFACE DE COMMANDEMENT - EXO_PRIME_ORCHESTRATOR")
    print("=" * 80)
    
    # Mode global
    print("\n[QUESTION 1] Mode global ?")
    print("  - DRAMA : Traitement audio complet (Brain Rot + Lip-Sync)")
    print("  - SILENT : Pas d'audio (skip lip-sync)")
    
    mode = None
    while mode not in ["DRAMA", "SILENT"]:
        try:
            user_input = input("Mode (DRAMA/SILENT) [DRAMA]: ").strip().upper()
            mode = user_input if user_input in ["DRAMA", "SILENT"] else "DRAMA"
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Interruption détectée. Utilisation des valeurs par défaut.")
            mode = "DRAMA"
            break
    
    # Nombre de variantes
    print("\n[QUESTION 2] Nombre de variantes par source vidéo ?")
    print("  - Recommandé : 3-5 variantes pour maximiser la couverture")
    
    num_variantes = None
    while num_variantes is None or num_variantes < 1:
        try:
            user_input = input("Nombre de variantes [3]: ").strip()
            num_variantes = int(user_input) if user_input else 3
            if num_variantes < 1:
                print("[WARNING] Le nombre de variantes doit être >= 1")
                num_variantes = None
        except ValueError:
            print("[WARNING] Entrée invalide. Utilisez un nombre entier.")
            num_variantes = None
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Interruption détectée. Utilisation des valeurs par défaut.")
            num_variantes = 3
            break
    
    print("=" * 80)
    print(f"[CONFIRMATION] Mode : {mode}")
    print(f"[CONFIRMATION] Variantes par source : {num_variantes}")
    print("=" * 80)
    
    return mode, num_variantes


def main():
    """
    Point d'entrée principal de l'Orchestrateur Suprême
    """
    # Parser les arguments en ligne de commande
    parser = argparse.ArgumentParser(
        description="EXO_PRIME_ORCHESTRATOR - Système Nerveux Central EXODUS"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode diagnostic : vérifie la structure sans exécuter les calculs lourds"
    )
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("EXO_PRIME_ORCHESTRATOR - SYSTÈME NERVEUX CENTRAL")
    print("La Voie Royale est mon guide, les 300k sont mon objectif.")
    print("=" * 80 + "\n")
    
    # Initialisation de l'Orchestrateur
    orchestrator = EXOPrimeOrchestrator()
    
    # MODE DRY-RUN : Diagnostic uniquement
    if args.dry_run:
        results = orchestrator.dry_run_diagnostic()
        # Exit code 0 si tout OK, 1 sinon
        all_ok = (
            results["assets"]["all_ok"] and
            results["environment"]["all_ok"] and
            results["permissions"]["all_ok"] and
            results["syntax"]["all_ok"]
        )
        sys.exit(0 if all_ok else 1)
    
    # MODE NORMAL : Exécution complète
    # INTERFACE DE COMMANDEMENT
    mode, num_variantes = interface_commandement()
    
    # Exécution du pipeline
    try:
        orchestrator.run(mode=mode, num_variantes=num_variantes)
    except KeyboardInterrupt:
        print("\n[INFO] Interruption utilisateur détectée. Arrêt de l'Orchestrateur.")
        orchestrator._print_final_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Erreur fatale de l'Orchestrateur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

