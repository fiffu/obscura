from enum import Enum
import os

from pydantic import BaseModel


class Environment(str, Enum):
    DEV = 'development'
    PROD = 'production'

    def __getattr__(self, attr: str) -> bool:
        if not attr.startswith('is_'):
            raise AttributeError(attr)

        enum_key = attr[3:].upper()
        return self.value == getattr(self, enum_key)


class Process(BaseModel):
    ENV: Environment
    DATABASE_URL: str
    API_TOKEN: str


PROCESS = Process(**{
    key: os.environ.get(key, None)
    for key in Process.model_fields
})
