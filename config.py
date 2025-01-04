from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the application.
    """

    openai_api_key: str
    tavily_api_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

