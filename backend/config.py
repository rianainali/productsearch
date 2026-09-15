from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    TOP_K_RESULTS: int = 5
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    VISION_MODEL: str = "gemini-2.5-flash"
    VISION_FALLBACK_MODELS: str = "gemini-2.0-flash,gemini-flash-latest"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
