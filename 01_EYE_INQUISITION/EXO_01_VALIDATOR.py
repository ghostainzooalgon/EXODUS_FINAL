#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXO_01_VALIDATOR.py - Segment 01 : VALIDATION PROGRAMMIQUE
Système EXODUS - Épreuve de Feu pour validation des données

Vérifie la conformité des fichiers et données générées par EXO_01_DNA_SCANNER.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class EXOValidator:
    """
    Validateur pour le Segment 01 - INQUISITION
    Vérifie la conformité des fichiers et données selon le schéma EXO_DATA_RAW.json
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialise le validateur
        
        Args:
            project_root: Racine du projet (défaut: répertoire actuel)
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Cherche la racine EXODUS_SYSTEM
            current = Path(__file__).resolve().parent
            while current.name != "EXODUS_SYSTEM" and current.parent != current:
                current = current.parent
            self.project_root = current if current.name == "EXODUS_SYSTEM" else Path.cwd()
        
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.success_count = 0
        
    def log_error(self, message: str):
        """Enregistre une erreur"""
        self.errors.append(message)
        print(f"[ERROR] : {message}")
    
    def log_warning(self, message: str):
        """Enregistre un avertissement"""
        self.warnings.append(message)
        print(f"[WARNING] : {message}")
    
    def log_success(self, message: str):
        """Enregistre un succès"""
        self.success_count += 1
        print(f"[SUCCESS] : {message}")
    
    def check_file_exists(self, file_path: Path, description: str) -> bool:
        """
        Vérifie l'existence d'un fichier
        
        Args:
            file_path: Chemin du fichier
            description: Description du fichier pour les messages
            
        Returns:
            True si le fichier existe, False sinon
        """
        if not file_path.exists():
            self.log_error(f"Fichier manquant : {description} ({file_path})")
            return False
        self.log_success(f"Fichier présent : {description}")
        return True
    
    def check_required_files(self) -> bool:
        """
        Vérifie la présence de tous les fichiers requis
        
        Returns:
            True si tous les fichiers sont présents
        """
        print("\n" + "="*60)
        print("ÉTAPE 1 : VÉRIFICATION DES FICHIERS REQUIS")
        print("="*60)
        
        all_present = True
        
        # Fichiers Python requis
        required_py_files = [
            (self.project_root / "01_EYE_INQUISITION" / "EXO_01_DNA_SCANNER.py", 
             "EXO_01_DNA_SCANNER.py (Scanner DNA)"),
        ]
        
        for file_path, description in required_py_files:
            if not self.check_file_exists(file_path, description):
                all_present = False
        
        # Fichiers JSON requis (schéma)
        required_schema = [
            (self.project_root / "SEGMENT_01" / "SCHEMA_JSON_DNA.md",
             "SCHEMA_JSON_DNA.md (Schéma de données)"),
        ]
        
        for file_path, description in required_schema:
            if not self.check_file_exists(file_path, description):
                all_present = False
        
        return all_present
    
    def find_data_json(self) -> Optional[Path]:
        """
        Cherche le fichier JSON de données brutes
        
        Returns:
            Chemin du fichier JSON trouvé, None sinon
        """
        # Chemins possibles (par ordre de priorité)
        possible_paths = [
            self.project_root / "Extraction_Data" / "mission_RAW.json",
            self.project_root / "01_EYE_INQUISITION" / "EXO_DATA_RAW.json",
            self.project_root / "EXO_DATA_RAW.json",
            self.project_root / "SEGMENT_01" / "EXO_DATA_RAW.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def validate_mouth_open_ratio(self, ratio: float, frame_num: int) -> bool:
        """
        Vérifie que mouth_open_ratio est entre 0.0 et 1.0
        
        Args:
            ratio: Valeur du ratio
            frame_num: Numéro de frame pour les messages
            
        Returns:
            True si valide
        """
        if ratio is None:
            self.log_error(f"Frame {frame_num} : mouth_open_ratio est None")
            return False
        
        if not isinstance(ratio, (int, float)):
            self.log_error(f"Frame {frame_num} : mouth_open_ratio n'est pas un nombre ({type(ratio)})")
            return False
        
        if ratio < 0.0 or ratio > 1.0:
            self.log_error(f"Frame {frame_num} : mouth_open_ratio hors limites ({ratio:.4f} - doit être entre 0.0 et 1.0)")
            return False
        
        return True
    
    def validate_pose_landmarks(self, pose_landmarks: Dict, frame_num: int) -> bool:
        """
        Vérifie que les landmarks de Pose sont au nombre de 33
        
        Args:
            pose_landmarks: Dictionnaire contenant all_33_landmarks
            frame_num: Numéro de frame pour les messages
            
        Returns:
            True si valide
        """
        if not pose_landmarks:
            self.log_warning(f"Frame {frame_num} : pose_landmarks est vide ou None")
            return False
        
        all_landmarks = pose_landmarks.get("all_33_landmarks", [])
        
        if not isinstance(all_landmarks, list):
            self.log_error(f"Frame {frame_num} : all_33_landmarks n'est pas une liste")
            return False
        
        count = len(all_landmarks)
        if count != 33:
            self.log_error(f"Frame {frame_num} : Nombre de landmarks Pose incorrect ({count} au lieu de 33)")
            return False
        
        # Vérification de la structure de chaque landmark
        for idx, landmark in enumerate(all_landmarks):
            required_keys = ["x", "y", "z", "visibility", "landmark_id"]
            for key in required_keys:
                if key not in landmark:
                    self.log_error(f"Frame {frame_num}, Landmark {idx} : Clé manquante '{key}'")
                    return False
        
        return True
    
    def validate_camera_metadata(self, camera_metadata: Dict, frame_num: int) -> bool:
        """
        Vérifie la présence de la métadonnée fps
        
        Args:
            camera_metadata: Dictionnaire contenant les métadonnées caméra
            frame_num: Numéro de frame pour les messages
            
        Returns:
            True si valide
        """
        if not camera_metadata:
            self.log_error(f"Frame {frame_num} : camera_metadata est vide ou None")
            return False
        
        if "fps" not in camera_metadata:
            self.log_error(f"Frame {frame_num} : Métadonnée 'fps' manquante dans camera_metadata")
            return False
        
        fps = camera_metadata["fps"]
        if not isinstance(fps, (int, float)):
            self.log_error(f"Frame {frame_num} : fps n'est pas un nombre ({type(fps)})")
            return False
        
        if fps <= 0:
            self.log_warning(f"Frame {frame_num} : fps invalide ({fps})")
        
        # Vérification de la résolution
        if "resolution" in camera_metadata:
            resolution = camera_metadata["resolution"]
            if "width" not in resolution or "height" not in resolution:
                self.log_warning(f"Frame {frame_num} : Résolution incomplète")
        
        return True
    
    def validate_face_landmarks(self, face_landmarks: Dict, frame_num: int) -> bool:
        """
        Vérifie la structure des landmarks faciaux (PROTOCOLE INNER-LIP)
        
        Args:
            face_landmarks: Dictionnaire contenant les landmarks faciaux
            frame_num: Numéro de frame pour les messages
            
        Returns:
            True si valide
        """
        if not face_landmarks:
            self.log_warning(f"Frame {frame_num} : face_landmarks est vide ou None")
            return False
        
        # Vérification des landmarks critiques (13-14)
        required_keys = ["upper_lip_center", "lower_lip_center", "mouth_open_ratio"]
        for key in required_keys:
            if key not in face_landmarks:
                self.log_error(f"Frame {frame_num} : Clé manquante '{key}' dans face_landmarks")
                return False
        
        # Vérification mouth_open_ratio
        if not self.validate_mouth_open_ratio(face_landmarks["mouth_open_ratio"], frame_num):
            return False
        
        # Vérification upper_lip_center (landmark 13)
        upper_lip = face_landmarks.get("upper_lip_center")
        if upper_lip:
            if upper_lip.get("landmark_id") != 13:
                self.log_error(f"Frame {frame_num} : upper_lip_center doit avoir landmark_id=13 (trouvé: {upper_lip.get('landmark_id')})")
                return False
        
        # Vérification lower_lip_center (landmark 14)
        lower_lip = face_landmarks.get("lower_lip_center")
        if lower_lip:
            if lower_lip.get("landmark_id") != 14:
                self.log_error(f"Frame {frame_num} : lower_lip_center doit avoir landmark_id=14 (trouvé: {lower_lip.get('landmark_id')})")
                return False
        
        return True
    
    def validate_json_structure(self, data: Dict) -> bool:
        """
        Valide la structure complète du JSON
        
        Args:
            data: Données JSON chargées
            
        Returns:
            True si la structure est valide
        """
        print("\n" + "="*60)
        print("ÉTAPE 2 : VALIDATION DE LA STRUCTURE JSON")
        print("="*60)
        
        valid = True
        
        # Vérification des clés principales
        required_top_keys = ["session_id", "timestamp"]
        for key in required_top_keys:
            if key not in data:
                self.log_error(f"Clé principale manquante : '{key}'")
                valid = False
        
        # Vérification des frames
        if "frames" in data:
            frames = data["frames"]
            if not isinstance(frames, list):
                self.log_error("'frames' n'est pas une liste")
                valid = False
            else:
                self.log_success(f"Nombre de frames détectées : {len(frames)}")
                
                # Validation de chaque frame
                print("\n" + "-"*60)
                print("VALIDATION FRAME PAR FRAME")
                print("-"*60)
                
                for idx, frame in enumerate(frames):
                    frame_num = frame.get("frame_number", idx)
                    
                    # Validation face_landmarks
                    if "face_landmarks" in frame:
                        if not self.validate_face_landmarks(frame["face_landmarks"], frame_num):
                            valid = False
                    else:
                        self.log_warning(f"Frame {frame_num} : face_landmarks manquant")
                    
                    # Validation pose_landmarks
                    if "pose_landmarks" in frame:
                        if not self.validate_pose_landmarks(frame["pose_landmarks"], frame_num):
                            valid = False
                    else:
                        self.log_warning(f"Frame {frame_num} : pose_landmarks manquant")
                    
                    # Validation camera_metadata
                    if "camera_metadata" in frame:
                        if not self.validate_camera_metadata(frame["camera_metadata"], frame_num):
                            valid = False
                    else:
                        self.log_error(f"Frame {frame_num} : camera_metadata manquant")
                        valid = False
        else:
            self.log_warning("Aucune frame trouvée dans le JSON (fichier vide ou structure différente)")
        
        return valid
    
    def validate_data_json(self) -> bool:
        """
        Valide le fichier JSON de données brutes
        
        Returns:
            True si le fichier est valide
        """
        print("\n" + "="*60)
        print("ÉTAPE 2 : VALIDATION DU FICHIER JSON DE DONNÉES")
        print("="*60)
        
        json_path = self.find_data_json()
        
        if not json_path:
            self.log_error("Fichier JSON de données brutes introuvable")
            self.log_warning("Chemins recherchés :")
            possible_paths = [
                "Extraction_Data/mission_RAW.json",
                "01_EYE_INQUISITION/EXO_DATA_RAW.json",
                "EXO_DATA_RAW.json",
                "SEGMENT_01/EXO_DATA_RAW.json",
            ]
            for path in possible_paths:
                self.log_warning(f"  - {path}")
            return False
        
        self.log_success(f"Fichier JSON trouvé : {json_path}")
        
        # Chargement du JSON
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.log_success("Fichier JSON valide (syntaxe correcte)")
        except json.JSONDecodeError as e:
            self.log_error(f"Erreur de syntaxe JSON : {e}")
            return False
        except Exception as e:
            self.log_error(f"Erreur lors de la lecture du fichier : {e}")
            return False
        
        # Validation de la structure
        return self.validate_json_structure(data)
    
    def run_validation(self) -> bool:
        """
        Exécute toutes les validations
        
        Returns:
            True si toutes les validations passent
        """
        print("\n" + "="*60)
        print("EXO_01_VALIDATOR - EPREUVE DE FEU")
        print("Systeme EXODUS - Segment 01 : INQUISITION")
        print("="*60)
        
        # Étape 1 : Vérification des fichiers
        files_ok = self.check_required_files()
        
        # Étape 2 : Validation du JSON (si présent)
        json_ok = self.validate_data_json()
        
        # Résumé
        print("\n" + "="*60)
        print("RÉSUMÉ DE LA VALIDATION")
        print("="*60)
        
        total_checks = self.success_count + len(self.errors) + len(self.warnings)
        print(f"Total de vérifications : {total_checks}")
        print(f"Succès : {self.success_count}")
        print(f"Erreurs : {len(self.errors)}")
        print(f"Avertissements : {len(self.warnings)}")
        
        if self.errors:
            print("\n" + "-"*60)
            print("ERREURS DETECTEES :")
            print("-"*60)
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n" + "-"*60)
            print("AVERTISSEMENTS :")
            print("-"*60)
            for warning in self.warnings:
                print(f"  - {warning}")
        
        # Résultat final
        all_valid = files_ok and json_ok and len(self.errors) == 0
        
        print("\n" + "="*60)
        if all_valid:
            print("[SUCCESS] : ADN VALIDÉ - PRÊT POUR LA FORGE")
            print("="*60)
        else:
            print("[FAILURE] : ADN INVALIDE - CORRECTIONS REQUISES")
            print("="*60)
        
        return all_valid


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EXO Validator - Segment 01")
    parser.add_argument("-r", "--root", help="Racine du projet EXODUS_SYSTEM")
    parser.add_argument("-j", "--json", help="Chemin spécifique vers le JSON de données")
    
    args = parser.parse_args()
    
    validator = EXOValidator(args.root)
    
    # Si un chemin JSON spécifique est fourni, on l'ajoute aux chemins de recherche
    if args.json:
        json_path = Path(args.json)
        if json_path.exists():
            # On force la validation de ce fichier
            validator.project_root = json_path.parent
            validator.validate_data_json()
        else:
            print(f"[ERROR] : Fichier JSON introuvable : {args.json}")
            sys.exit(1)
    else:
        success = validator.run_validation()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

