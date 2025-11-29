import argparse
import json
import logging
import multiprocessing
import signal
import sys
from pathlib import Path
from typing import Dict, List, Union

from src.services.config import PipelineConfig
from src.services.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages camera processes lifecycle."""
    
    def __init__(self):
        self._processes: List[multiprocessing.Process] = []
    
    def add(self, process: multiprocessing.Process):
        """Add process to manager."""
        self._processes.append(process)
    
    def stop_all(self):
        """Stop all processes gracefully."""
        logger.info("Stopping all cameras...")
        for process in self._processes:
            self._stop_process(process)
        sys.exit(0)
    
    def _stop_process(self, process: multiprocessing.Process):
        """Stop single process."""
        if not process.is_alive():
            return
        logger.info(f"Terminating camera process {process.pid}")
        process.terminate()
        process.join(timeout=5)
        if not process.is_alive():
            return
        logger.warning(f"Force killing process {process.pid}")
        process.kill()
    
    def wait_all(self):
        """Wait for all processes to complete."""
        try:
            for process in self._processes:
                process.join()
        except KeyboardInterrupt:
            self.stop_all()


class ConfigParser:
    """Parses and validates camera configuration."""
    
    @staticmethod
    def parse_source(source) -> Union[str, int]:
        """Parse source to int if possible, otherwise return as-is."""
        try:
            return int(source)
        except (ValueError, TypeError):
            return source
    
    @staticmethod
    def get_resize(config: Dict):
        """Get resize tuple from config if present."""
        resize = config.get('resize')
        return tuple(resize) if resize else None
    
    @staticmethod
    def create_pipeline_config(config: Dict, source: Union[str, int]) -> PipelineConfig:
        """Create PipelineConfig from dictionary config."""
        return PipelineConfig(
            source=source,
            output=config.get('output'),
            device=config.get('device'),
            det_model=config.get('det_model'),
            imgsz=config.get('imgsz'),
            conf_threshold=config.get('conf_threshold'),
            conf_person=config.get('conf_person'),
            conf_train=config.get('conf_train'),
        )


class CameraRunner:
    """Runs a single camera pipeline."""
    
    def __init__(self, parser: ConfigParser):
        self._parser = parser
    
    def run(self, camera_id: str, config: Dict, show: bool = False):
        """Run camera pipeline."""
        source = self._validate_source(config, camera_id)
        if source is None:
            return
        
        source = self._parser.parse_source(source)
        logger.info(f"Starting camera {camera_id} with source: {source}")
        
        try:
            pipeline_config = self._parser.create_pipeline_config(config, source)
            pipeline = Pipeline(pipeline_config, camera_id=camera_id)
            resize = self._parser.get_resize(config)
            
            pipeline.run(
                max_frames=config.get('max_frames'),
                resize=resize,
                show=show
            )
        except KeyboardInterrupt:
            logger.info(f"Camera {camera_id} interrupted")
        except Exception as e:
            logger.error(f"Camera {camera_id} error: {e}", exc_info=True)
    
    @staticmethod
    def _validate_source(config: Dict, camera_id: str):
        """Validate source in config."""
        source = config.get('source')
        if source is None:
            logger.error(f"Camera {camera_id}: No source specified")
        return source


class ConfigLoader:
    """Loads camera configurations from files."""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Dict]:
        """Load cameras configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                raise
    
    @staticmethod
    def exists(config_path: str) -> bool:
        """Check if config file exists."""
        return Path(config_path).exists()
    
    @staticmethod
    def create_default(output_path: str):
        """Create default camera configuration file."""
        default_config = {
            "camera-1": {
                "source": "data/raw/ремонты.mov",
                "name": "Camera 1",
                "output": None,
                "device": None,
                "det_model": None,
                "imgsz": None,
                "conf_threshold": None,
                "conf_person": None,
                "conf_train": None,
                "resize": None,
                "max_frames": None
            }
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        logger.info(f"Created default config at {output_path}")


class CameraManager:
    """Main manager for multiple camera streams."""
    
    def __init__(self):
        self._process_manager = ProcessManager()
        self._config_loader = ConfigLoader()
        self._config_parser = ConfigParser()
        self._camera_runner = CameraRunner(self._config_parser)
    
    def setup_signals(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, lambda s, f: self._process_manager.stop_all())
        signal.signal(signal.SIGTERM, lambda s, f: self._process_manager.stop_all())
    
    def load_cameras(self, args) -> Dict[str, Dict]:
        """Load camera configurations from args."""
        if args.camera and args.source:
            return self._create_single_camera_config(args.camera, args.source)
        if args.config:
            return self._load_from_file(args.config)
        return {}
    
    def _create_single_camera_config(self, camera_id: str, source: str) -> Dict[str, Dict]:
        """Create config for single camera mode."""
        return {
            camera_id: {
                "source": source,
                "name": camera_id
            }
        }
    
    def _load_from_file(self, config_path: str) -> Dict[str, Dict]:
        """Load cameras from config file."""
        if not self._config_loader.exists(config_path):
            logger.error(f"Config file not found: {config_path}")
            logger.info("Use --create-config to create a default config")
            return {}
        return self._config_loader.load(config_path)
    
    def start_cameras(self, cameras: Dict[str, Dict], show: bool):
        """Start all camera processes."""
        logger.info(f"Starting {len(cameras)} camera(s)...")
        for camera_id, config in cameras.items():
            self._start_camera(camera_id, config, show)
        logger.info("All cameras started. Monitoring...")
    
    def _start_camera(self, camera_id: str, config: Dict, show: bool):
        """Start a single camera process."""
        process = multiprocessing.Process(
            target=self._camera_runner.run,
            args=(camera_id, config, show),
            name=f"Camera-{camera_id}",
            daemon=False
        )
        process.start()
        self._process_manager.add(process)
        logger.info(f"Started camera {camera_id} (PID: {process.pid})")
    
    def wait_for_completion(self):
        """Wait for all cameras to complete."""
        self._process_manager.wait_all()
        logger.info("All cameras stopped")


def _create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Camera Manager - Run multiple camera streams simultaneously"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="/app/config/cameras.json",
        help="Path to JSON configuration file with cameras"
    )
    parser.add_argument(
        "--camera",
        type=str,
        help="Run single camera (requires --source)"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Video source for single camera mode"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show video windows (not recommended in production)"
    )
    parser.add_argument(
        "--create-config",
        type=str,
        help="Create default configuration file at specified path"
    )
    return parser


def _validate_args(args, parser: argparse.ArgumentParser) -> bool:
    """Validate command line arguments."""
    if args.camera and args.source:
        return True
    if args.config:
        return True
    parser.print_help()
    logger.error("Either --config or --camera with --source must be specified")
    return False


def main():
    """Main entry point for camera manager."""
    parser = _create_argument_parser()
    args = parser.parse_args()
    
    if args.create_config:
        ConfigLoader.create_default(args.create_config)
        return
    
    if not _validate_args(args, parser):
        return
    
    manager = CameraManager()
    manager.setup_signals()
    
    cameras = manager.load_cameras(args)
    if not cameras:
        logger.error("No cameras configured")
        return
    
    manager.start_cameras(cameras, args.show)
    manager.wait_for_completion()


if __name__ == "__main__":
    main()

