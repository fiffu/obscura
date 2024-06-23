from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from itertools import cycle
import random
import uuid

from obscura.repo import Repository
from obscura.model import Record, Variant
from obscura.process import PROCESS


class SlugExpiredError(ValueError):
    pass


class SlugNotFoundError(ValueError):
    pass


class Service:
    def __init__(self, db: Repository) -> None:
        self.db = db

    @staticmethod
    def now() -> datetime:
        return datetime.now()
    
    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_salt() -> str:
        return str(uuid.uuid4())    
        
    def save(self, variant: Variant, payload: str) -> str:
        valid_since = self.now()
        valid_until = valid_since + timedelta(days=7)

        record = Record(
            id=self.generate_id(),
            variant=variant,
            payload=payload,
            salt=self.generate_salt(),
        )

        self.db.save(record)
        return self.generate_slugs(record, valid_since, valid_until)

    def recover(self, slug: str) -> Record:
        record_id, salt, valid_since, valid_until = Slug.parse(slug)

        now = self.now()
        is_valid = valid_since < now < valid_until
        if not is_valid:
            raise SlugExpiredError
        
        record = self.db.find(record_id, salt)
        if not record:
            raise SlugNotFoundError
        
        return record

    @staticmethod
    def generate_slugs(record: Record, *validities: datetime):
        slugs = []

        n = len(validities)
        if (n % 2) != 0:
            # Should provide an even number of validities here
            raise TypeError(f'expected even number of validities, got: {n}')
        
        for i in range(0, n, 2):
            valid_since, valid_until = validities[i], validities[i+1]
            if valid_since > valid_until:
                raise TypeError(f'valid_since ({valid_since.isoformat()}) at index {i} should precede '
                                f'valid_until ({valid_until.isoformat()}) at index {i+1})')

            slug = Slug.generate(record.salt, record.id, valid_since, valid_until)
            slugs.append(slug)

        return slugs

class Slug:
    STRING_CODEC = 'utf-8'
    STRING_DELIM = '|'
    key = PROCESS.API_TOKEN.encode(STRING_CODEC)

    @staticmethod
    def nonce() -> int:
        return int(random.randint(0, 1<<16))
    
    @staticmethod
    def to_base64(b: bytes) -> str:
        return b64encode(b).decode()

    @staticmethod
    def from_base64(s: str) -> bytes:
        return b64decode(s + '==')

    @staticmethod
    def parse_timestamp(ts: str) -> datetime:
        return datetime.fromtimestamp(float(ts))
    
    @classmethod
    def xor(cls, bs: bytes) -> bytes:
        return bytes(
            b ^ k
            for b, k in zip(bs, cycle(cls.key))
        )

    @classmethod
    def generate(cls, salt: str,  record_id: str, valid_since: datetime, valid_until: datetime) -> str:
        fields = [salt, record_id, valid_since.timestamp(), valid_until.timestamp(), cls.nonce()]

        clear = cls.STRING_DELIM.join(map(str, fields))
        clear_bytes = clear.encode(cls.STRING_CODEC)

        crypt = cls.xor(clear_bytes)
        return cls.to_base64(crypt).strip('=')
    
    @classmethod
    def parse(cls, slug: str):
        crypt = cls.from_base64(slug)

        clear_bytes = cls.xor(crypt)
        clear = clear_bytes.decode(cls.STRING_CODEC)
        fields = clear.split(cls.STRING_DELIM)

        salt, record_id, valid_since, valid_until, _ = fields
        valid_since = cls.parse_timestamp(valid_since)
        valid_until = cls.parse_timestamp(valid_until)

        return record_id, salt, valid_since, valid_until
    
