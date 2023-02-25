from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "terraformer"
    debug: bool = False
