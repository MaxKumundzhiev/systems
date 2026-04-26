import logging

from llm import LLMLoader, ModelLoadError
from settings import settings

from fastapi import FastAPI
from contextlib import asynccontextmanager

from llama_cpp import Llama

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up...")
        app.state.model = LLMLoader(settings=settings).load()
        yield
    except ModelLoadError as e:
        logger.error(f"Failed to load model: {e}")
        raise
    finally:
        logger.info("Shutting down...")
        app.state.model = None


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    if app.state.model is None:
        return {"status": "error", "detail": "model not loaded"}
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
