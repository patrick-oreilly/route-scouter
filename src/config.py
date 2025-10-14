from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    google_cloud_project: str
    google_application_credentials: str
    google_maps_api_key: str
    openweather_api_key: str
    google_api_key: str
    log_level: str = "INFO"

settings = Settings()