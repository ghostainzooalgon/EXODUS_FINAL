#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXO_01_DNA_SCANNER.py - Segment 01 : INQUISITION
Système EXODUS - Extraction de données brutes depuis vidéo source

PROTOCOLE INNER-LIP : Landmarks 13-14 (centres des lèvres, pas les coins)
"""

import cv2
import mediapipe as mp
import numpy as np
import whisper
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math
import urllib.request
from tqdm import tqdm
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision


class EXODNAScanner:
    """
    Scanner DNA universel pour extraction de données brutes (mission_RAW.json)
    Utilise MediaPipe Tasks PoseLandmarker (multi-pose), FaceMesh (Inner-Lip),
    OpenCV Optical Flow, Whisper
    """
    
    # Landmarks MediaPipe FaceMesh (PROTOCOLE INNER-LIP)
    UPPER_LIP_CENTER_ID = 13  # Centre lèvre supérieure (Inner Lip)
    LOWER_LIP_CENTER_ID = 14  # Centre lèvre inférieure (Inner Lip)
    
    def __init__(self, drive_root: str, video_path: Optional[str] = None):
        """
        Initialise le scanner DNA
        
        DOCTRINE DE L'ANCRE UNIQUE :
        - Tous les chemins sont basés sur drive_root
        - INPUT_DIR = drive_root / "00_INPUT" (vidéos sources)
        - DATA_DIR = drive_root / "01_BUFFER" (sortie JSON)
        
        Args:
            drive_root: Racine du système de fichiers (ancre unique)
            video_path: Chemin vers la vidéo source (optionnel, si None scanne INPUT_DIR)
        """
        # CONSTANTES DE CHEMINS (pathlib pour compatibilité Linux)
        self.drive_root = Path(drive_root)
        self.INPUT_DIR = self.drive_root / "00_INPUT"
        self.DATA_DIR = self.drive_root / "01_BUFFER"
        self.TOOLS_DIR = self.drive_root / "04_TOOLS"
        
        # Création des dossiers si nécessaire
        self.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Déterminer le chemin vidéo
        if video_path:
            self.video_path = Path(video_path)
        else:
            # Scanner INPUT_DIR pour trouver la première vidéo
            video_files = list(self.INPUT_DIR.glob("*.mp4")) + list(self.INPUT_DIR.glob("*.MP4"))
            if not video_files:
                raise FileNotFoundError(f"Aucune vidéo trouvée dans {self.INPUT_DIR}")
            self.video_path = video_files[0]
            print(f"[INFO] Vidéo détectée automatiquement : {self.video_path.name}")
        
        # Chemin de sortie standardisé (SCHEMA UNIVERSEL)
        self.output_path = self.DATA_DIR / "mission_RAW.json"
        
        # Initialisation MediaPipe (FaceMesh classique + PoseLandmarker Tasks)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Modèles MediaPipe
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            # LEGION DYNAMIQUE : autorise N visages (limite haute pour perf)
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # SCANNER UNIVERSEL : PoseLandmarker (multi-pose, jusqu'à 5 corps)
        self.pose_model_path = self._ensure_pose_model()
        self.pose_landmarker = self._create_pose_landmarker()
        
        # Initialisation Whisper (LOCAL - ZÉRO COÛT)
        print("[INFO] Chargement du modele Whisper (local, gratuit)...")
        self.whisper_model = whisper.load_model("base")  # base, small, medium, large
        print("[OK] Whisper charge")
        
        # Variables de tracking
        self.session_id = f"EXO_SESSION_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.frame_number = 0
        # LEGION DYNAMIQUE : métriques simples (pas un tracking inter-frame complet)
        self.max_actors_detected = 0
        self.prev_gray = None
        self.max_mouth_distance = 0.0  # Pour normalisation mouth_open_ratio
        
        # Données accumulées (SCANNER UNIVERSEL)
        self.camera_motion: List[Dict] = []
        self.actors_data: Dict[str, Dict[str, List[Dict]]] = {}
        self.audio_transcription: Optional[Dict] = None
        self.video_metadata: Dict = {}

    # ------------------------------------------------------------------
    #  MOTEUR DE POSE : PoseLandmarker (Tasks API)
    # ------------------------------------------------------------------
    def _ensure_pose_model(self) -> Path:
        """
        Vérifie la présence du modèle pose_landmarker_heavy.task,
        sinon le télécharge automatiquement dans 04_TOOLS.
        """
        model_path = self.TOOLS_DIR / "pose_landmarker_heavy.task"
        if model_path.exists():
            return model_path

        url = (
            "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
            "pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"
        )
        print(f"[INFO] Modèle PoseLandmarker introuvable. Téléchargement depuis : {url}")
        try:
            with urllib.request.urlopen(url) as response, open(model_path, "wb") as out_file:
                data = response.read()
                out_file.write(data)
            print(f"[SUCCESS] Modèle téléchargé : {model_path}")
        except Exception as e:
            print(f"[ERROR] Échec du téléchargement du modèle PoseLandmarker : {e}")
            raise

        return model_path

    def _create_pose_landmarker(self):
        """
        Crée l'instance PoseLandmarker (multi-poses, num_poses=5)
        """
        base_options = mp_python.BaseOptions(
            model_asset_path=str(self.pose_model_path)
        )
        options = mp_vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=5,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        print("[INFO] Initialisation PoseLandmarker (num_poses=5)...")
        return mp_vision.PoseLandmarker.create_from_options(options)
        
    def calculate_mouth_open_ratio(self, upper_lip: np.ndarray, lower_lip: np.ndarray) -> float:
        """
        Calcule l'ouverture de la bouche basée sur la distance VERTICALE
        entre les landmarks 13 (upper_lip_center) et 14 (lower_lip_center)
        
        PROTOCOLE INNER-LIP : Distance verticale uniquement (pas euclidienne)
        
        Args:
            upper_lip: Coordonnées [x, y, z] du landmark 13
            lower_lip: Coordonnées [x, y, z] du landmark 14
            
        Returns:
            Ratio normalisé 0.0 (fermé) à 1.0 (ouvert maximum)
        """
        if upper_lip is None or lower_lip is None:
            return 0.0
        
        # Distance VERTICALE uniquement (différence en Y)
        vertical_distance = abs(upper_lip[1] - lower_lip[1])
        
        # Mise à jour du maximum pour normalisation
        if vertical_distance > self.max_mouth_distance:
            self.max_mouth_distance = vertical_distance
        
        # Normalisation : 0.0 = fermé, 1.0 = ouvert maximum observé
        if self.max_mouth_distance > 0:
            ratio = min(vertical_distance / self.max_mouth_distance, 1.0)
        else:
            ratio = 0.0
        
        return float(ratio)
    
    def extract_face_landmarks(self, face_landmarks) -> Dict:
        """
        Extrait les landmarks faciaux (468 points MediaPipe FaceMesh)
        Focus sur landmarks 13-14 (PROTOCOLE INNER-LIP)
        
        Args:
            face_landmarks: Objet MediaPipe FaceMesh landmarks
            
        Returns:
            Dictionnaire avec upper_lip_center, lower_lip_center, mouth_open_ratio, all_468_landmarks
        """
        if not face_landmarks:
            return {
                "upper_lip_center": None,
                "lower_lip_center": None,
                "mouth_open_ratio": 0.0,
                "all_468_landmarks": []
            }
        
        # Extraction de tous les landmarks (468 points)
        all_landmarks = []
        for idx, landmark in enumerate(face_landmarks.landmark):
            all_landmarks.append({
                "x": float(landmark.x),
                "y": float(landmark.y),
                "z": float(landmark.z),
                "landmark_id": idx
            })
        
        # Extraction des landmarks critiques (13-14) - PROTOCOLE INNER-LIP
        upper_lip = None
        lower_lip = None
        
        if len(face_landmarks.landmark) > self.UPPER_LIP_CENTER_ID:
            upper_landmark = face_landmarks.landmark[self.UPPER_LIP_CENTER_ID]
            upper_lip = np.array([upper_landmark.x, upper_landmark.y, upper_landmark.z])
        
        if len(face_landmarks.landmark) > self.LOWER_LIP_CENTER_ID:
            lower_landmark = face_landmarks.landmark[self.LOWER_LIP_CENTER_ID]
            lower_lip = np.array([lower_landmark.x, lower_landmark.y, lower_landmark.z])
        
        # Calcul mouth_open_ratio (distance verticale)
        mouth_open_ratio = self.calculate_mouth_open_ratio(upper_lip, lower_lip)
        
        # Structure de sortie
        face_data = {
            "upper_lip_center": {
                "x": float(upper_lip[0]) if upper_lip is not None else None,
                "y": float(upper_lip[1]) if upper_lip is not None else None,
                "z": float(upper_lip[2]) if upper_lip is not None else None,
                "landmark_id": self.UPPER_LIP_CENTER_ID
            } if upper_lip is not None else None,
            "lower_lip_center": {
                "x": float(lower_lip[0]) if lower_lip is not None else None,
                "y": float(lower_lip[1]) if lower_lip is not None else None,
                "z": float(lower_lip[2]) if lower_lip is not None else None,
                "landmark_id": self.LOWER_LIP_CENTER_ID
            } if lower_lip is not None else None,
            "mouth_open_ratio": mouth_open_ratio,
            "all_468_landmarks": all_landmarks
        }
        
        return face_data
    
    def extract_pose_landmarks(self, pose_landmarks) -> Dict:
        """
        Extrait les landmarks de pose (33 points MediaPipe Pose)
        
        Args:
            pose_landmarks: Liste de landmarks MediaPipe Pose (déjà une liste avec PoseLandmarker)
            
        Returns:
            Dictionnaire avec all_33_landmarks
        """
        if not pose_landmarks:
            return {"all_33_landmarks": []}
        
        all_landmarks = []
        for idx, landmark in enumerate(pose_landmarks):
            all_landmarks.append({
                "x": float(landmark.x),
                "y": float(landmark.y),
                "z": float(landmark.z),
                "visibility": float(landmark.visibility),
                "landmark_id": idx
            })
        
        return {"all_33_landmarks": all_landmarks}
    
    def calculate_optical_flow(self, frame: np.ndarray) -> Dict:
        """
        Calcule l'Optical Flow pour détecter les mouvements de caméra
        
        Args:
            frame: Frame actuelle (BGR)
            
        Returns:
            Dictionnaire avec magnitude, angle, flow_vectors
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_gray is None:
            self.prev_gray = gray
            return {
                "magnitude": 0.0,
                "angle": 0.0,
                "flow_vectors": []
            }
        
        # Calcul du flux optique (Lucas-Kanade)
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Magnitude et angle
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        avg_magnitude = float(np.mean(magnitude))
        avg_angle = float(np.mean(angle))
        
        # Échantillonnage des vecteurs de flux (pour réduire la taille)
        h, w = flow.shape[:2]
        step = max(1, min(h, w) // 20)  # ~400 points max
        flow_vectors = []
        for y in range(0, h, step):
            for x in range(0, w, step):
                fx, fy = flow[y, x]
                flow_vectors.append([float(fx), float(fy)])
        
        self.prev_gray = gray
        
        return {
            "magnitude": avg_magnitude,
            "angle": avg_angle,
            "flow_vectors": flow_vectors
        }
    
    def transcribe_audio(self, video_path: str) -> Dict:
        """
        Transcription audio avec Whisper (LOCAL - ZÉRO COÛT)
        
        Args:
            video_path: Chemin vers la vidéo
            
        Returns:
            Dictionnaire avec text, confidence, timestamp
        """
        print("[INFO] Transcription audio avec Whisper (local)...")
        
        try:
            result = self.whisper_model.transcribe(
                str(video_path),
                language="fr",  # ou "en" selon besoin
                task="transcribe"
            )
            
            # Calcul de la confiance moyenne
            segments = result.get("segments", [])
            if segments:
                avg_confidence = sum(s.get("no_speech_prob", 0.5) for s in segments) / len(segments)
                confidence = 1.0 - avg_confidence  # Inversion : plus bas = plus confiant
            else:
                confidence = 0.5
            
            transcription = {
                "text": result.get("text", ""),
                "confidence": float(confidence),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            print("[OK] Transcription terminee")
            return transcription
            
        except Exception as e:
            print(f"⚠️ Erreur transcription: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def process_video(self):
        """
        Traite la vidéo complète : extraction frame par frame (SCANNER UNIVERSEL)
        
        - Multi-pose (PoseLandmarker Tasks)
        - FaceMesh pour l'ouverture de bouche (13-14)
        - Optical Flow pour mouvements de caméra
        - Structure de sortie :
          {
            "metadata": {...},
            "camera_motion": [...],
            "actors": {
               "0": {"pose_frames": [...], "mouth_frames": [...]},
               "1": {...}
            }
          }
        """
        if not self.video_path.exists():
            raise FileNotFoundError(f"Vidéo non trouvée: {self.video_path}")
        
        print(f"[INFO] Ouverture de la video: {self.video_path}")
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Impossible d'ouvrir la vidéo: {self.video_path}")
        
        # Métadonnées vidéo
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = float(total_frames / fps) if fps > 0 else 0.0
        
        print(f"[INFO] Resolution: {width}x{height}, FPS: {fps}, Frames: {total_frames}")
        
        # MÉTADONNÉES GLOBALES
        self.video_metadata = {
            "session_id": self.session_id,
            "source_video": str(self.video_path),
            "fps": float(fps),
            "resolution": {"width": width, "height": height},
            "total_frames": int(total_frames),
            "duration_seconds": duration_sec,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pose_model": "pose_landmarker_heavy",
        }
        
        frame_count = 0
        
        # Barre de progression (tqdm)
        pbar = tqdm(total=total_frames if total_frames > 0 else None,
                    desc="SCANNER UNIVERSEL",
                    unit="frame")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Timestamp de la frame (ms) pour PoseLandmarker
            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            timestamp_iso = datetime.now(timezone.utc).isoformat()
            
            # Conversion BGR -> RGB pour MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # ---------------------------
            # 1) POSES (PoseLandmarker)
            # ---------------------------
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )
            pose_result = self.pose_landmarker.detect_for_video(
                mp_image, int(timestamp_ms)
            )
            pose_landmarks_list = pose_result.pose_landmarks or []

            # Calcul de la position X pour chaque pose (utilise le nez = landmark 0)
            pose_candidates = []
            for pose_lmk in pose_landmarks_list:
                if not pose_lmk:
                    continue
                nose = pose_lmk[0]
                center_x = float(nose.x)
                pose_candidates.append((center_x, pose_lmk))

            # Trier de gauche à droite pour IDs stables
            pose_candidates.sort(key=lambda item: item[0])

            # Initialiser acteurs pour cette frame
            frame_actor_pose: Dict[str, Dict] = {}

            for idx, (center_x, pose_lmk) in enumerate(pose_candidates):
                actor_id = str(idx)  # ID temporaire basé sur la position X
                # Initialiser structure globale si nécessaire
                if actor_id not in self.actors_data:
                    self.actors_data[actor_id] = {
                        "pose_frames": [],
                        "mouth_frames": [],
                    }
                # Extraire les 33 points XYZ (et visibility)
                pose_data = self.extract_pose_landmarks(pose_lmk)
                pose_frame = {
                    "frame_number": frame_count,
                    "timestamp": timestamp_iso,
                    "landmarks": pose_data.get("all_33_landmarks", []),
                    "center_x": center_x,
                }
                self.actors_data[actor_id]["pose_frames"].append(pose_frame)
                frame_actor_pose[actor_id] = pose_frame
            
            # ---------------------------
            # 2) FACEMESH (Inner-Lip 13-14)
            # ---------------------------
            face_results = self.face_mesh.process(rgb_frame)
            faces = face_results.multi_face_landmarks or []

            # Calcul X bouche et mouth_open_ratio pour chaque visage
            face_infos = []
            for face_landmarks in faces:
                face_data = self.extract_face_landmarks(face_landmarks)
                upper = face_data.get("upper_lip_center")
                lower = face_data.get("lower_lip_center")
                if upper and lower:
                    center_x = float((upper["x"] + lower["x"]) / 2.0)
                elif upper:
                    center_x = float(upper["x"])
                else:
                    # fallback: prendre landmark 0 si dispo
                    if face_data.get("all_468_landmarks"):
                        center_x = float(face_data["all_468_landmarks"][0]["x"])
                    else:
                        continue
                face_infos.append(
                    {
                        "center_x": center_x,
                        "mouth_open_ratio": float(face_data.get("mouth_open_ratio", 0.0)),
                    }
                )

            # Associer chaque bouche au corps le plus proche (en X)
            for face_info in face_infos:
                if not frame_actor_pose:
                    # Aucun corps détecté cette frame → on associe à actor "0"
                    actor_id = "0"
                else:
                    fx = face_info["center_x"]
                    # Trouver l'acteur avec center_x le plus proche
                    best_actor = None
                    best_dist = None
                    for aid, pose_frame in frame_actor_pose.items():
                        px = pose_frame.get("center_x", fx)
                        d = abs(px - fx)
                        if best_dist is None or d < best_dist:
                            best_dist = d
                            best_actor = aid
                    actor_id = best_actor if best_actor is not None else "0"

                if actor_id not in self.actors_data:
                    self.actors_data[actor_id] = {
                        "pose_frames": [],
                        "mouth_frames": [],
                    }

                mouth_frame = {
                    "frame_number": frame_count,
                    "timestamp": timestamp_iso,
                    "mouth_open_ratio": face_info["mouth_open_ratio"],
                }
                self.actors_data[actor_id]["mouth_frames"].append(mouth_frame)
            
            # Mise à jour métriques
            self.max_actors_detected = max(
                self.max_actors_detected, len(frame_actor_pose)
            )

            # ---------------------------
            # 3) CAMERA MOTION (Optical Flow)
            # ---------------------------
            optical_flow_data = self.calculate_optical_flow(frame)
            self.camera_motion.append(
                {
                    "frame_number": frame_count,
                    "timestamp": timestamp_iso,
                    "optical_flow": optical_flow_data,
                }
            )

            frame_count += 1
            pbar.update(1)
        
        cap.release()
        pbar.close()
        print(f"[OK] Traitement video termine: {frame_count} frames")
        
        # Transcription audio (une seule fois pour toute la vidéo)
        self.audio_transcription = self.transcribe_audio(self.video_path)
        
        # Note: La transcription audio est ajoutée dans output_data sous "audio_transcription_global"
        # (architecture Multi-Acteurs : pas de frames_data, utilisation de actors_data)
    
    def save_output(self):
        """
        Sauvegarde les données dans mission_RAW.json (structure universelle)
        """
        # Création du répertoire parent si nécessaire
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "metadata": {
                **self.video_metadata,
                "max_actors_detected": int(self.max_actors_detected),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "camera_motion": self.camera_motion,
            "actors": self.actors_data,
            "audio_transcription_global": self.audio_transcription,
        }
        
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sauvegarde: {e}")
            raise
        
        print(f"[OK] Donnees sauvegardees: {self.output_path}")
        print(f"[INFO] Total frames: {len(self.camera_motion)}")


def main():
    """
    Point d'entrée principal
    
    DOCTRINE DE L'ANCRE UNIQUE :
    - Accepte --drive-root (obligatoire)
    - Optionnellement accepte un chemin vidéo spécifique
    - Sinon, scanne automatiquement 00_INPUT/ pour les vidéos
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="EXO DNA Scanner - Segment 01")
    parser.add_argument(
        "--drive-root",
        type=str,
        required=True,
        help="Racine du système de fichiers (ancre unique). Défaut Colab: /content/drive/MyDrive/EXODUS_SYSTEM"
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Chemin vers une vidéo spécifique (optionnel, sinon scanne 00_INPUT/)"
    )
    
    args = parser.parse_args()
    
    # Détection automatique du défaut Colab si non fourni
    drive_root = args.drive_root
    if not drive_root:
        default_colab_root = Path("/content/drive/MyDrive/EXODUS_SYSTEM")
        if default_colab_root.exists():
            drive_root = str(default_colab_root)
            print(f"[INFO] Drive Root détecté automatiquement (Colab) : {drive_root}")
        else:
            print("[ERROR] --drive-root est requis ou le défaut Colab doit exister")
            sys.exit(1)
    
    try:
        # AFFICHAGE DES CHEMINS DÉTECTÉS
        print("=" * 80)
        print("[DOCTRINE DE L'ANCRE UNIQUE] - Segment 01 - Chemins détectés :")
        print("=" * 80)
        print(f"  RACINE (ANCRE)     : {drive_root}")
        print(f"  INPUT_DIR          : {Path(drive_root) / '00_INPUT'}")
        print(f"  DATA_DIR           : {Path(drive_root) / '01_BUFFER'}")
        print("=" * 80)
        
        # Initialisation du scanner
        scanner = EXODNAScanner(drive_root, args.video)
        
        # Traitement
        scanner.process_video()
        scanner.save_output()
        
        print(f"[SUCCESS] Mission accomplie - EXO_DATA_RAW.json généré dans {scanner.output_path}")
    except Exception as e:
        print(f"[ERROR] Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

