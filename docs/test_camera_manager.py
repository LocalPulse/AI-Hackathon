#!/usr/bin/env python3
"""
Camera Manager Setup Verification Script

This script verifies that the camera manager is properly configured
and all required dependencies are available before deployment.
"""

import sys
from pathlib import Path


def check_config_file() -> str | None:
    """Check for camera configuration file existence.
    
    Returns:
        Path to configuration file if found, None otherwise.
    """
    config_paths = [
        Path("config/cameras.json"),
        Path("cameras.json"),
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            print(f"[OK] Configuration file found: {config_path}")
            return str(config_path)
    
    print("[ERROR] Configuration file not found")
    print("  Create config/cameras.json or use --create-config option")
    return None


def check_video_file() -> bool:
    """Check for video file existence.
    
    Returns:
        True if video file exists, False otherwise.
    """
    video_path = Path("data/raw/ремонты.mov")
    if video_path.exists():
        print(f"[OK] Video file found: {video_path}")
        return True
    else:
        print(f"[WARNING] Video file not found: {video_path}")
        print("  Ensure file exists or update path in configuration")
        return False


def test_import() -> bool:
    """Test if camera_manager module can be imported.
    
    Returns:
        True if import successful, False otherwise.
    """
    try:
        from src.services.camera_manager import CameraManager
        print("[OK] camera_manager module imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("  Install dependencies: pip install -r requirements.txt")
        return False


def main():
    """Main verification function."""
    print("=" * 70)
    print("Camera Manager Setup Verification")
    print("=" * 70)
    print()
    
    # Test module import
    print("1. Testing module import...")
    import_success = test_import()
    print()
    
    if not import_success:
        print("[FAILED] Module import check failed. Fix dependencies before proceeding.")
        sys.exit(1)
    
    # Check configuration
    print("2. Checking configuration files...")
    config_path = check_config_file()
    print()
    
    # Check video file
    print("3. Checking video files...")
    has_video = check_video_file()
    print()
    
    # Summary
    print("=" * 70)
    if config_path and has_video:
        print("[SUCCESS] All checks passed")
        print()
        print("To start camera manager, use:")
        print(f"  python -m src.services.camera_manager --config {config_path}")
        print()
        print("Or for single camera mode:")
        print("  python -m src.services.camera_manager --camera camera-1 --source data/raw/ремонты.mov")
        sys.exit(0)
    else:
        print("[FAILED] Some checks failed")
        print("  Fix errors before deployment")
        if not config_path:
            print("  - Missing configuration file")
        if not has_video:
            print("  - Missing video file (may be acceptable if using camera index)")
        sys.exit(1)


if __name__ == "__main__":
    main()
