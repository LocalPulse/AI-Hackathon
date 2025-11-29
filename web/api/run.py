#!/usr/bin/env python3
"""
Run script for FastAPI application.
Can be run from any directory.
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "web.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT / "web" / "api")]
    )
