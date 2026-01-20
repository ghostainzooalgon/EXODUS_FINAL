"""
EXO_EYE_TEST_RAM_v1.0.py
Script de test de consommation RAM pour SEGMENT 01
Système cible : 8Go RAM
Objectif : Vérifier que le système peut fonctionner sur Colab gratuit / Warp Cloud
"""

import psutil
import os
import sys
from pathlib import Path

def get_memory_info():
    """Récupère les informations de mémoire système"""
    memory = psutil.virtual_memory()
    return {
        'total_gb': memory.total / (1024**3),
        'available_gb': memory.available / (1024**3),
        'used_gb': memory.used / (1024**3),
        'percent': memory.percent
    }

def check_requirements():
    """Vérifie que les dépendances critiques sont installées"""
    required_modules = [
        'cv2',  # OpenCV
        'mediapipe',
        'whisper',
        'numpy'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return missing

def estimate_whisper_memory(model_size='large'):
    """Estime la consommation mémoire de Whisper selon le modèle"""
    model_sizes = {
        'tiny': 0.1,   # GB
        'base': 0.2,
        'small': 0.5,
        'medium': 1.0,
        'large': 2.0,
        'large-v2': 2.0,
        'large-v3': 2.0
    }
    return model_sizes.get(model_size, 2.0)

def estimate_opencv_memory(video_resolution='1920x1080', fps=60):
    """Estime la consommation mémoire d'OpenCV pour traitement vidéo"""
    # Approximation : ~50MB par frame en mémoire pour traitement
    width, height = map(int, video_resolution.split('x'))
    pixels_per_frame = width * height
    bytes_per_frame = pixels_per_frame * 3  # RGB
    mb_per_frame = bytes_per_frame / (1024**2)
    
    # Buffer pour 2 secondes de vidéo
    buffer_frames = fps * 2
    buffer_mb = mb_per_frame * buffer_frames
    
    return buffer_mb / 1024  # GB

def estimate_mediapipe_memory():
    """Estime la consommation mémoire de MediaPipe"""
    # MediaPipe est optimisé, consommation faible
    return 0.2  # GB

def run_memory_test():
    """Exécute le test de mémoire complet"""
    print("=" * 60)
    print("EXO_EYE - TEST DE CONSOMMATION RAM")
    print("Système cible : 8Go RAM")
    print("=" * 60)
    print()
    
    # Informations système
    mem_info = get_memory_info()
    print(f"📊 MÉMOIRE SYSTÈME :")
    print(f"   Total : {mem_info['total_gb']:.2f} GB")
    print(f"   Disponible : {mem_info['available_gb']:.2f} GB")
    print(f"   Utilisée : {mem_info['used_gb']:.2f} GB ({mem_info['percent']:.1f}%)")
    print()
    
    # Vérification des dépendances
    print("🔍 VÉRIFICATION DES DÉPENDANCES :")
    missing = check_requirements()
    if missing:
        print(f"   ❌ Modules manquants : {', '.join(missing)}")
        print("   ⚠️  Installez-les avec : pip install -r requirements.txt")
    else:
        print("   ✅ Tous les modules requis sont installés")
    print()
    
    # Estimation de consommation
    print("💾 ESTIMATION DE CONSOMMATION RAM :")
    
    whisper_mem = estimate_whisper_memory('large')
    print(f"   Whisper Large : ~{whisper_mem:.2f} GB")
    
    opencv_mem = estimate_opencv_memory('1920x1080', 60)
    print(f"   OpenCV (vidéo 1080p@60fps) : ~{opencv_mem:.2f} GB")
    
    mediapipe_mem = estimate_mediapipe_memory()
    print(f"   MediaPipe : ~{mediapipe_mem:.2f} GB")
    
    # Overhead système
    system_overhead = 1.0  # GB pour OS et autres processus
    print(f"   Overhead système : ~{system_overhead:.2f} GB")
    
    total_estimated = whisper_mem + opencv_mem + mediapipe_mem + system_overhead
    print()
    print(f"   📈 TOTAL ESTIMÉ : ~{total_estimated:.2f} GB")
    print()
    
    # Recommandations
    print("💡 RECOMMANDATIONS :")
    if total_estimated > mem_info['available_gb']:
        print(f"   ⚠️  Consommation estimée ({total_estimated:.2f} GB) > RAM disponible ({mem_info['available_gb']:.2f} GB)")
        print("   Solutions :")
        print("   - Utiliser Whisper Medium au lieu de Large (-0.5 GB)")
        print("   - Traiter la vidéo par chunks")
        print("   - Utiliser Google Colab Pro (16GB RAM)")
    else:
        print(f"   ✅ Consommation estimée ({total_estimated:.2f} GB) < RAM disponible ({mem_info['available_gb']:.2f} GB)")
        print("   Le système devrait fonctionner correctement")
    
    print()
    print("=" * 60)
    print("Test terminé")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_memory_test()
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        sys.exit(1)

