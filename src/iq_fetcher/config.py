import sys
from typing import Optional
from pathlib import Path

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

from iq_fetcher.utils import resolve_path, find_project_root as get_base_dir


base_dir = get_base_dir(__file__)
dotenv_path = resolve_path(str(Path("config") / ".env"))
load_dotenv(dotenv_path=dotenv_path)


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=dotenv_path, env_file_encoding="utf-8", extra="ignore"
    )

    iq_server_url: str = Field(validation_alias="IQ_SERVER_URL")
    iq_username: str = Field(validation_alias="IQ_USERNAME")
    iq_password: str = Field(validation_alias="IQ_PASSWORD")
    organization_id: Optional[str] = Field(None, validation_alias="ORGANIZATION_ID")
    output_dir: str = Field("raw_reports", validation_alias="OUTPUT_DIR")
    num_workers: int = Field(8, ge=1, validation_alias="NUM_WORKERS")

    @field_validator("iq_username", "iq_password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("credentials must not be empty")
        return v


def get_config() -> Config:
    try:
        return Config()  # type: ignore
    except ValidationError as e:
        missing_vars = []
        for error in e.errors():
            if error["type"] == "missing":
                field_name = error["loc"][0] if error["loc"] else "unknown"
                missing_vars.append(field_name)
        if missing_vars:
            print(
                f"💥 Missing required environment variables: {', '.join(missing_vars)}. "
                "Please check your .env file or environment settings.",
                file=sys.stderr,
            )
        else:
            print(f"💥 Configuration validation error: {e}", file=sys.stderr)
        sys.exit(1)
