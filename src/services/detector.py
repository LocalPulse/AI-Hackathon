from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:
    from src.utils.weights_manager import MODEL_URLS, download_file
except ImportError:
    MODEL_URLS = {}
    download_file = None

logger = logging.getLogger(__name__)

MODEL_ALIASES = {
    "medium": "yolo11m",
    "m": "yolo11m",
    "large": "yolo11l",
    "l": "yolo11l",
    "x": "yolo11x",
}


def detect_device(requested: Optional[str] = None) -> str:
    if requested:
        return requested
    
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def resolve_model_path(model: str) -> str:
    """Resolve model path, creating models directory if needed."""
    name = MODEL_ALIASES.get(model, model)
    
    # Check direct path
    if Path(name).exists():
        return name
    
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    for suffix in ["", ".pt"]:
        candidate = models_dir / f"{name}{suffix}"
        if candidate.exists():
            return str(candidate)
    
    return name


def _download_if_needed(model_name: str) -> Optional[str]:
    if model_name not in MODEL_URLS or download_file is None:
        return None
    
    url = MODEL_URLS[model_name]
    dest = Path("models") / Path(url).name
    
    if dest.exists():
        return str(dest)
    
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading {model_name} to {dest}")
        download_file(url, dest)
        return str(dest)
    except Exception as e:
        logger.warning(f"Download failed for {model_name}: {e}")
        return None


def load_model(model: str = "yolo11m", device: Optional[str] = None):
    resolved = resolve_model_path(model)
    
    downloaded = _download_if_needed(resolved)
    if downloaded:
        resolved = downloaded
    
    logger.info(f"Loading model: {resolved}")
    
    try:
        from ultralytics import YOLO
        import os
        import shutil
        
        models_dir = Path("models").absolute()
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Temporarily set ULTRALYTICS_HOME to models directory
        old_home = os.environ.get("ULTRALYTICS_HOME")
        try:
            os.environ["ULTRALYTICS_HOME"] = str(models_dir)
            yolo = YOLO(resolved)
        finally:
            if old_home is not None:
                os.environ["ULTRALYTICS_HOME"] = old_home
            elif "ULTRALYTICS_HOME" in os.environ:
                del os.environ["ULTRALYTICS_HOME"]
        
        if not str(resolved).startswith(str(models_dir)):
            model_name = resolved.split("/")[-1].split("\\")[-1]
            if not model_name.endswith(".pt"):
                model_name += ".pt"
            
            default_locations = [
                Path(model_name),  
                Path.cwd() / model_name,  
                Path.home() / ".ultralytics" / "weights" / model_name,  
            ]
            
            target_path = models_dir / model_name
            for default_loc in default_locations:
                if default_loc.exists() and default_loc != target_path and not target_path.exists():
                    logger.info(f"Moving model from {default_loc} to {target_path}")
                    try:
                        shutil.move(str(default_loc), str(target_path))
                        # Update resolved path to point to models
                        resolved = str(target_path)
                        break
                    except Exception as e:
                        logger.warning(f"Failed to move model: {e}")
        
        # Move model to device if specified
        if device:
            try:
                import torch
                if hasattr(yolo, "model") and yolo.model is not None:
                    yolo.model.to(torch.device(device))
            except Exception:
                pass  # Non-fatal: use default device
        
        return yolo
    except Exception as e:
        raise RuntimeError(f"Failed to load model '{model}': {e}") from e


__all__ = ["detect_device", "resolve_model_path", "load_model"]
