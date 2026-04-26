import logging

from settings import settings
from prompts.system import SYSTEM_PROMPT
from llm import LLMLoader, ModelLoadError


from fastapi import FastAPI
from contextlib import asynccontextmanager

from llama_cpp import Llama, ChatCompletionRequestMessage, ChatCompletion

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


@app.post("/chat")
async def chat(user_query: str):
    model: Llama = app.state.model

    messages: list[ChatCompletionRequestMessage] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    response: ChatCompletion = model.create_chat_completion(  # type: ignore[assignment]
        messages=messages,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
    )
    return {
        "system": SYSTEM_PROMPT,
        "user": user_query,
        "assistant": response["choices"][0]["message"]["content"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
