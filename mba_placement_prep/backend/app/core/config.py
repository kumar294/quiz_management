from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-7"
    database_url: str = "sqlite:///./prep.db"
    storage_dir: str = "./storage"
    log_level: str = "INFO"
    scraper_user_agent: str = "GLIM-PrepBot/0.1"
    scraper_rate_limit_per_min: int = 20


settings = Settings()
