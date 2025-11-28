from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "detection": {
        "model": "yolo11m",
        "image_size": 640,
        "device": None,
    },
    "confidence": {
        "threshold": 0.25,
        "person": 0.35,
        "vehicle": 0.65,
    },
    "nms": {
        "iou_threshold": 0.45,
    },
    "tracker": {
        "iou_threshold": 0.2,
        "max_lost": 45,
        "use_prediction": True,
    },
    "activity": {
        "window": 15,
        "person": {
            "speed_threshold": 15.0,
        },
        "vehicle": {
            "displacement_threshold": 8.0,
            "min_history": 5,
        },
    },
    "clothing": {
        "enabled": True,
        "high_vis": {
            "h_min": 5,
            "h_max": 35,
            "s_min": 100,
            "v_min": 100,
            "coverage": 0.03,
        },
    },
    "video": {
        "default_fps": 25.0,
        "resize": [640, 480],
    },
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    config = DEFAULT_CONFIG.copy()
    
    if config_path is None:
        # Search for config.yaml in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return config
    
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            file_config = yaml.safe_load(f) or {}
        
        # Deep merge with defaults
        config = _deep_merge(config, file_config)
        logger.info(f"Loaded configuration from {config_path}")
    except ImportError:
        logger.warning("PyYAML not installed. Install with: pip install pyyaml")
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}, using defaults")
    
    return config


def _deep_merge(base: Dict, update: Dict) -> Dict:
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


# Global config instance
_config: Optional[Dict[str, Any]] = None


def get_config(reload: bool = False) -> Dict[str, Any]:
    global _config
    
    if _config is None or reload:
        _config = load_config()
    
    return _config


__all__ = ["load_config", "get_config", "DEFAULT_CONFIG"]

