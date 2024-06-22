import uuid
from typing import Optional

from obscura.model import Record, Variant


class Database:
    def __init__(self, dsn):
        self.store = {}

    @staticmethod
    def generate_pk() -> str:
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_salt() -> str:
        return str(uuid.uuid4())    

    def save(self, variant: Variant, payload: str) -> Record:
        record = Record(
            id=self.generate_pk(),
            variant=str(variant),
            payload=payload,
            salt=self.generate_salt(),
        )
        key = (record.id, record.salt)
        self.store[key] = record
        return record

    def find(self, record_id: str, salt: str) -> Optional[Record]:
        key = (record_id, salt)
        return self.store.get(key)