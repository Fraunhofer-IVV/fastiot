from typing import List

from pydantic.main import BaseModel


class InfrastructureServiceComposeInfo(BaseModel):
    name: str
    image: str
    environment: List[str]
    ports: List[str]
    volumes: List[str]
