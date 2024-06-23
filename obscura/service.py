from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
from itertools import cycle
import random
import uuid

from obscura import errors
from obscura.logger import log
from obscura.model import Record, Variant
from obscura.process import PROCESS
from obscura.repo import Repository


class Service:
    def __init__(self, db: Repository) -> None:
        self.db = db

    def save(self, variant: Variant, payload: str) -> str:
        record = Record(
            id=Generate.record_id(),
            variant=variant,
            payload=payload,
            salt=Generate.record_salt(),
        )
        self.db.save(record)
        return record

    def recover(self, slug: str) -> Record:
        record_id, salt, valid_since, valid_secs = Slug.parse(slug)
        log.info('id=%s, valid_since=%s, valid_secs=%s', record_id, valid_since, valid_secs)

        now = datetime.now()
        is_valid = valid_since < now < now + timedelta(seconds=valid_secs)
        if not is_valid:
            raise errors.SlugInvalidTimeError(slug=slug, record_id=record_id, salt=salt)

        record = self.db.find(record_id, salt)
        if not record:
            raise errors.SlugNotFoundError(slug=slug, record_id=record_id, salt=salt)

        return record

    @classmethod
    def generate_daily_slugs(cls, record: Record, num_days: int) -> list[str]:
        now = datetime.now()
        valid_secs = int(timedelta(1).total_seconds())

        validities = []
        for i in range(num_days):
            valid_since = now + timedelta(days=i)
            slug = Slug.generate(record.salt, record.id, valid_since, valid_secs)

            validities.append({
                'ref': slug,
                'usable_after': valid_since.astimezone(timezone.utc),
                'usable_duration_seconds': valid_secs,
            })

        return validities


class Generate:
    @staticmethod
    def record_id() -> str:
        return str(uuid.uuid4())

    @classmethod
    def record_salt(cls) -> str:
        return str(cls.nonce())[::-1]

    @staticmethod
    def nonce(length=32) -> int:
        return random.randint(0, 1<<length)


class Slug:
    STRING_CODEC = 'utf-8'
    STRING_DELIM = '|'
    key = PROCESS.API_TOKEN.encode(STRING_CODEC)

    @staticmethod
    def to_base64(b: bytes) -> str:
        return b64encode(b).decode()

    @staticmethod
    def from_base64(s: str) -> bytes:
        return b64decode(s + '==')

    @classmethod
    def xor(cls, bs: bytes) -> bytes:
        return bytes(
            b ^ k
            for b, k in zip(bs, cycle(cls.key))
        )

    @classmethod
    def generate(cls, salt: str,  record_id: str, valid_since: datetime, valid_secs: int) -> str:
        fields = [Generate.nonce(), valid_since.timestamp(), valid_secs, salt, record_id]

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

        _, valid_since, valid_secs, salt, record_id = fields
        valid_since = datetime.fromtimestamp(float(valid_since))
        valid_secs = int(valid_secs)

        return record_id, salt, valid_since, valid_secs

