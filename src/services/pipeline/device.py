import logging
from typing import Optional
import torch

logger = logging.getLogger(__name__)


def detect_device(requested: Optional[str] = None) -> str:
    """Detect available compute device (CUDA or CPU)."""
    if requested:
        return requested
    
    if torch is None:
        return "cpu"
    
    if not torch.cuda.is_available():
        return "cpu"
    
    logger.info(f"CUDA: {torch.cuda.get_device_name(0)}")
    return "cuda"

