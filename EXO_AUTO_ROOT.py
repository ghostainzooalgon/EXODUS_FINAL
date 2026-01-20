#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXO_AUTO_ROOT.py - Boussole Auto-Root (PROTOCOLE LOGISTIQUE_MIROIR)
Détection automatique de l'environnement (Colab vs Windows local)

DOCTRINE :
- Si /content/drive existe → Environnement Colab (Google Drive monté)
- Sinon → Environnement local Windows/Linux
- Retourne toujours le chemin racine approprié pour EXODUS_SYSTEM
"""

import os
from pathlib import Path
from typing import Optional


def detect_exodus_root() -> Path:
    """
    BOUSSOLE AUTO-ROOT : Détecte automatiquement la racine EXODUS
    
    PROTOCOLE LOGISTIQUE_MIROIR :
    1. Si /content/drive existe → Colab (utiliser Drive)
    2. Sinon → Local (utiliser chemin du script)
    
    Returns:
        Path vers la racine EXODUS_SYSTEM
    """
    # Détection Colab : Vérifier si /content/drive existe
    colab_drive_path = Path("/content/drive")
    if colab_drive_path.exists():
        # Environnement Colab : Utiliser Google Drive
        drive_exodus_path = colab_drive_path / "MyDrive" / "EXODUS_SYSTEM"
        
        # Vérifier si EXODUS_SYSTEM existe sur Drive
        if drive_exodus_path.exists():
            print(f"[AUTO-ROOT] Environnement Colab détecté - Drive: {drive_exodus_path}")
            return drive_exodus_path
        else:
            # Si Drive monté mais EXODUS_SYSTEM n'existe pas, utiliser /content/EXODUS_SYSTEM (clone GitHub)
            content_exodus_path = Path("/content/EXODUS_SYSTEM")
            if content_exodus_path.exists():
                print(f"[AUTO-ROOT] Environnement Colab détecté - Clone GitHub: {content_exodus_path}")
                return content_exodus_path
            else:
                # Fallback : créer sur Drive
                drive_exodus_path.mkdir(parents=True, exist_ok=True)
                print(f"[AUTO-ROOT] Environnement Colab détecté - Création Drive: {drive_exodus_path}")
                return drive_exodus_path
    
    # Environnement local : Utiliser le chemin du script appelant
    # On cherche le fichier qui appelle cette fonction (remonter jusqu'à EXODUS_SYSTEM)
    import inspect
    try:
        frame = inspect.currentframe()
        # Remonter la pile d'appels pour trouver le script appelant
        caller_frame = frame.f_back
        if caller_frame:
            caller_file = Path(caller_frame.f_globals.get('__file__', ''))
            if caller_file.exists():
                # Remonter jusqu'à trouver EXODUS_SYSTEM
                current = caller_file.resolve().parent
                while current != current.parent:  # Jusqu'à la racine
                    if (current / "EXO_PRIME_ORCHESTRATOR.py").exists() or \
                       (current / "01_EYE_INQUISITION").exists():
                        print(f"[AUTO-ROOT] Environnement local détecté - Racine: {current}")
                        return current
                    current = current.parent
    except (AttributeError, ValueError):
        # Si inspect échoue, utiliser le chemin courant
        pass
    
    # Fallback : Chercher depuis le chemin courant
    current = Path.cwd()
    while current != current.parent:  # Jusqu'à la racine
        if (current / "EXO_PRIME_ORCHESTRATOR.py").exists() or \
           (current / "01_EYE_INQUISITION").exists():
            print(f"[AUTO-ROOT] Environnement local détecté (fallback) - Racine: {current}")
            return current
        current = current.parent
    
    # Fallback ultime : Chemin courant
    fallback_path = Path.cwd()
    print(f"[AUTO-ROOT] Fallback ultime - Chemin courant: {fallback_path}")
    return fallback_path


def is_colab_environment() -> bool:
    """
    Vérifie si l'environnement est Google Colab
    
    Returns:
        True si Colab, False sinon
    """
    return Path("/content/drive").exists()


def is_windows_environment() -> bool:
    """
    Vérifie si l'environnement est Windows
    
    Returns:
        True si Windows, False sinon
    """
    import platform
    return platform.system() == "Windows"

