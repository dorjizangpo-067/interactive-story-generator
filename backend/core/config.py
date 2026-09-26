from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    API_PREFIX: str
    DEBUG: bool = False

    ALLOWED_ORIGIN: str
    GOOGLE_API_KEY: SecretStr

    @field_validator("ALLOWED_ORIGIN")
    def prase_allowed_origin(cls, v: str) -> list[str]:
        return v.split(",") if v else []

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()  # type: ignore[call-arg]
