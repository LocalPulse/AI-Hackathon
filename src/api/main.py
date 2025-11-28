from __future__ import annotations

import logging
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    BaseModel = object
    HTTPException = Exception

logger = logging.getLogger(__name__)


if FastAPI:
    app = FastAPI(
        title="AI-Hackathon API",
        description="YOLO detection and tracking pipeline API",
        version="1.0.0"
    )
else:
    app = None


class HealthResponse(BaseModel if FastAPI else object):
    status: str
    device: str


class ProcessRequest(BaseModel if FastAPI else object):
    source: str
    output: Optional[str] = None
    det_model: str = "yolo11m"
    conf_person: float = 0.35
    conf_train: float = 0.65


class ProcessResponse(BaseModel if FastAPI else object):
    status: str
    frames: int
    fps: float


def _get_device() -> str:
    try:
        from src.services.pipeline import detect_device
        return detect_device()
    except Exception:
        return "unknown"


if app:
    @app.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(status="ok", device=_get_device())

    @app.get("/")
    async def root():
        return {
            "name": "AI-Hackathon API",
            "version": "1.0.0",
            "endpoints": ["/health", "/process"]
        }

    @app.post("/process", response_model=ProcessResponse)
    async def process(request: ProcessRequest):
        try:
            from src.services.config import PipelineConfig
            from src.services.pipeline import Pipeline
            
            config = PipelineConfig(
                source=request.source,
                output=request.output,
                det_model=request.det_model,
                conf_person=request.conf_person,
                conf_train=request.conf_train
            )
            
            pipeline = Pipeline(config)
            pipeline.run(show=False)
            
            return ProcessResponse(status="completed", frames=0, fps=0.0)
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


def main():
    if app is None:
        print("FastAPI not installed. Install with: pip install fastapi uvicorn")
        return
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
