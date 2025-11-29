from typing import Optional, Dict


def get_class_name(names: Optional[Dict], cls_id: int) -> Optional[str]:
    if names is None:
        return None
    
    if isinstance(names, dict):
        return names.get(cls_id)
    
    try:
        return names[cls_id]
    except (IndexError, KeyError):
        return None

