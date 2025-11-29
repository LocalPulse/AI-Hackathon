from __future__ import annotations

import torch
import logging
import os
import shutil

from pathlib import Path
from ultralytics import YOLO # type: ignore
from typing import Optional

from src.utils.weights_manager import MODEL_URLS, download_file  # type: ignore

logger = logging.getLogger(__name__)

MODEL_ALIASES = {
    "medium": "yolo11m",
    "m": "yolo11m",
    "large": "yolo11l",
    "l": "yolo11l",
    "x": "yolo11x",
}

DEFAULT_MODEL_DIR = Path("models")
DEFAULT_ULTRALYTICS_WEIGHTS = Path.home() / ".ultralytics" / "weights"


def detect_device(requested: Optional[str] = None) -> str:
    if requested:
        return requested
    
    if torch is None:
        return "cpu"
    
    return "cuda" if torch.cuda.is_available() else "cpu"


class ModelPathResolver:
    def __init__(self, models_dir: Path = DEFAULT_MODEL_DIR):
        self.models_dir = models_dir.absolute()
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def normalize_name(self, model: str) -> str:
        """Convert model alias to canonical name."""
        return MODEL_ALIASES.get(model.lower(), model)
    
    def find_existing_path(self, model_name: str) -> Optional[Path]:
        """Find existing model file in common locations."""
        if Path(model_name).exists():
            return Path(model_name).absolute()
        
        for suffix in ["", ".pt"]:
            candidate = self.models_dir / f"{model_name}{suffix}"
            if candidate.exists():
                return candidate
        
        return None
    
    def resolve(self, model: str) -> str:
        """Resolve model path, creating models directory if needed."""
        normalized = self.normalize_name(model)
        existing = self.find_existing_path(normalized)
        
        return str(existing) if existing else normalized


class ModelDownloader:
    def __init__(self, models_dir: Path = DEFAULT_MODEL_DIR):
        self.models_dir = models_dir.absolute()
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, model_name: str) -> Optional[Path]:
        """Download model if URL is available and file doesn't exist."""
        if model_name not in MODEL_URLS or download_file is None:
            return None
        
        url = MODEL_URLS[model_name]
        dest = self.models_dir / Path(url).name
        
        if dest.exists():
            return dest
        
        return self._perform_download(model_name, url, dest)
    
    def _perform_download(self, model_name: str, url: str, dest: Path) -> Optional[Path]:
        if download_file is None:
            return None
        
        try:
            logger.info(f"Downloading {model_name} to {dest}")
            download_file(url, dest)
            return dest
        except Exception as e:
            logger.warning(f"Download failed for {model_name}: {e}")
            return None


class ModelOrganizer:
    def __init__(self, models_dir: Path = DEFAULT_MODEL_DIR):
        self.models_dir = models_dir.absolute()
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def ensure_in_models_dir(self, model_path: str) -> str:
        """Ensure model is in models directory, move if needed."""
        path = Path(model_path).absolute()
        
        if self._is_in_models_dir(path):
            return str(path)
        
        # Extract model name from path (same logic as old version)
        model_name = path.name
        if "/" in str(path) or "\\" in str(path):
            model_name = str(path).replace("\\", "/").split("/")[-1]
        
        if not model_name.endswith(".pt"):
            model_name += ".pt"
        
        target = self.models_dir / model_name
        
        if target.exists():
            return str(target)
        
        source = self._find_model_in_default_locations(model_name)
        if source and source != target and not target.exists():
            return self._move_model(source, target)
        
        return str(path)
    
    def _is_in_models_dir(self, path: Path) -> bool:
        try:
            return path.resolve().is_relative_to(self.models_dir)
        except (AttributeError, ValueError):
            return str(path).startswith(str(self.models_dir))
    
    
    def _find_model_in_default_locations(self, model_name: str) -> Optional[Path]:
        locations = [
            Path(model_name),
            Path.cwd() / model_name,
            DEFAULT_ULTRALYTICS_WEIGHTS / model_name,
        ]
        
        for location in locations:
            if location.exists():
                return location.absolute()
        
        return None
    
    def _move_model(self, source: Path, target: Path) -> str:
        try:
            logger.info(f"Moving model from {source} to {target}")
            shutil.move(str(source), str(target))
            return str(target)
        except Exception as e:
            logger.warning(f"Failed to move model: {e}")
            return str(source)


class UltralyticsEnvironment:
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir.absolute()
        self.old_home: Optional[str] = None
    
    def __enter__(self):
        self.old_home = os.environ.get("ULTRALYTICS_HOME")
        os.environ["ULTRALYTICS_HOME"] = str(self.models_dir)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_home is not None:
            os.environ["ULTRALYTICS_HOME"] = self.old_home
        elif "ULTRALYTICS_HOME" in os.environ:
            del os.environ["ULTRALYTICS_HOME"]


def _move_model_to_device(yolo_model, device: Optional[str]) -> None:
    """Move YOLO model to specified device."""
    if not device or torch is None:
        return
    
    try:
        if hasattr(yolo_model, "model") and yolo_model.model is not None:
            yolo_model.model.to(torch.device(device))
    except Exception as e:
        logger.debug(f"Failed to move model to device {device}: {e}")


def load_model(model: str = "yolo11m", device: Optional[str] = None):
    resolver = ModelPathResolver()
    downloader = ModelDownloader()
    organizer = ModelOrganizer()
    
    resolved_path = resolver.resolve(model)
    downloaded_path = downloader.download(resolved_path)
    
    if downloaded_path:
        resolved_path = str(downloaded_path)
    
    logger.info(f"Loading model: {resolved_path}")
    
    if YOLO is None:
        raise RuntimeError("ultralytics package is not installed")
    
    try:
        with UltralyticsEnvironment(organizer.models_dir):
            yolo_model = YOLO(resolved_path)
        
        organized_path = organizer.ensure_in_models_dir(resolved_path)
        if organized_path != resolved_path:
            logger.debug(f"Model organized to: {organized_path}")
        
        _move_model_to_device(yolo_model, device)
        return yolo_model
    
    except Exception as e:
        raise RuntimeError(f"Failed to load model '{model}': {e}") from e


def resolve_model_path(model: str) -> str:
    resolver = ModelPathResolver()
    return resolver.resolve(model)


__all__ = ["detect_device", "resolve_model_path", "load_model"]
