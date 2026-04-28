from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",  # always points to project root
        env_file_encoding="utf-8",
    )

    # HuggingFace
    hf_model_repo_id: str = "bartowski/Llama-3.2-1B-Instruct-GGUF"
    hf_model_filename: str = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    fs_model_path: Path = Path("models")

    # Inference
    n_ctx: int = 2048
    n_threads: int = 8
    max_tokens: int = 512
    temperature: float = 0.7

    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000


settings = Settings()
