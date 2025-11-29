import argparse
import logging

from src.services.config import PipelineConfig
from src.services.pipeline import Pipeline


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    parser = argparse.ArgumentParser(description="Video detection and tracking")
    parser.add_argument("--source", "-s", default=0, help="Video source")
    parser.add_argument("--camera-id", type=str, help="Camera identifier (for multi-camera setup)")
    parser.add_argument("--output", "-o", help="Output video path")
    parser.add_argument("--device", "-d", help="Device: cuda or cpu")
    parser.add_argument("--det-model", default=None, help="Detection model (default: from config.yaml)")
    parser.add_argument("--show", action="store_true", help="Show video")
    parser.add_argument("--imgsz", type=int, default=None, help="Image size (default: from config.yaml)")
    parser.add_argument("--conf-threshold", type=float, default=None, help="Confidence threshold (default: from config.yaml)")
    parser.add_argument("--conf-person", type=float, default=None, help="Person confidence (default: from config.yaml)")
    parser.add_argument("--conf-train", type=float, default=None, help="Vehicle confidence (default: from config.yaml)")
    parser.add_argument("--resize", nargs=2, type=int, default=None, metavar=("W", "H"), help="Resize dimensions (default: from config.yaml)")
    parser.add_argument("--max-frames", type=int)
    args = parser.parse_args()
    
    try:
        source = int(args.source)
    except ValueError:
        source = args.source
    
    config = PipelineConfig(
        source=source,
        output=args.output,
        device=args.device,
        det_model=args.det_model,
        imgsz=args.imgsz,
        conf_threshold=args.conf_threshold,
        conf_person=args.conf_person,
        conf_train=args.conf_train,
    )
    
    resize = tuple(args.resize) if args.resize else None
    camera_id = args.camera_id or None
    
    Pipeline(config, camera_id=camera_id).run(
        max_frames=args.max_frames,
        resize=resize,
        show=args.show
    )


if __name__ == "__main__":
    main()
