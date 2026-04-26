import logging
from typing import Optional

from settings import (
    Settings,
    settings as env_settings,
)  # Settings for type hint, settings as default

from llama_cpp import Llama
from huggingface_hub import hf_hub_download

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class ModelLoadError(Exception):
    pass


class ModelDownloadError(Exception):
    pass


class LLMLoader:

    def __init__(
        self,
        settings: Optional[Settings] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._logger = logger if logger else logging.getLogger(__name__)
        self._settings = settings if settings else env_settings

    def _download_model(self) -> str:
        try:
            self._logger.info(
                f"Downloading model {self._settings.hf_model_filename} from {self._settings.hf_model_repo_id}..."
            )
            path = hf_hub_download(
                repo_id=self._settings.hf_model_repo_id,
                filename=self._settings.hf_model_filename,
                local_dir=self._settings.fs_model_path,
            )
            self._logger.info(f"Model downloaded to {path}")
            return path
        except Exception as e:
            self._logger.error(f"Download attempt failed: {e}")
            raise ModelDownloadError(f"Failed to download model: {e}") from e

    def _init_model(self, model_path: str) -> Llama:
        try:
            self._logger.info("Loading model into memory...")
            model = Llama(
                model_path=model_path,
                n_ctx=self._settings.n_ctx,
                n_threads=self._settings.n_threads,
                verbose=False,
            )
            self._logger.info("Model loaded successfully")
            return model
        except Exception as e:
            self._logger.error(f"Failed to initialize model: {e}")
            raise ModelLoadError(f"Failed to initialize model: {e}") from e

    def load(self) -> Llama:
        download_with_retry = retry(
            retry=retry_if_exception_type(ModelDownloadError),
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True,
        )(self._download_model)

        path = download_with_retry()
        model = self._init_model(path)
        return model
