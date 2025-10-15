from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    google_cloud_project: str
    google_application_credentials: str
    google_maps_api_key: str
    openweather_api_key: str
    gemini_api_key: str
    anthropic_api_key: str
    openai_api_key: str
    grok_api_key: str
    ollama_api_base: str = "http://localhost:11434"

    log_level: str = "INFO"

settings = Settings()