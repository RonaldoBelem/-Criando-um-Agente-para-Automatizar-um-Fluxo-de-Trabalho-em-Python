from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    TRELLO_API_KEY: str
    TRELLO_API_TOKEN: str

Settings = _Settings()
