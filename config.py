from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import os


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

    gemini_model:str
    openai_model:str
    grok_model:str
    mistral_model:str 
    gpt_oss_model:str

    log_level: str = "INFO"

settings = Settings()

def setup_logging():
    """ Config for the logging setup"""

    log_level_int = getattr(logging,settings.log_level.upper(), logging.INFO)
    LOG_FILE_PATH = 'test_log.log'

    if(os.path.exists(LOG_FILE_PATH)):
        print(f"Logging will append to :{LOG_FILE_PATH}")
    else:
        print(f"New file created for logging: {LOG_FILE_PATH}")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s',
        filename=LOG_FILE_PATH,
        filemode='a'
    )