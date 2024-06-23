from typing import Optional

from obscura.model import Record, Variant
from obscura.db.client import Client


class Repository:
    def __init__(self, dsn):
        self.db = Client.connect(dsn)
        self.db.migrate()

    def save(self, record: Record):
        with self.db as tx:
            tx.execute('''
                INSERT INTO records(id, salt, variant, payload)
                VALUES(?, ?, ?, ?)
            ''', record.id, record.salt, record.variant.value, record.payload)

    def find(self, record_id: str, salt: str) -> Optional[Record]:
        for row in self.db.execute('''
            SELECT id, salt, variant, payload FROM records
            WHERE id=? AND salt=?
            LIMIT 1
        ''', record_id, salt):
            if not row:
                return None

            id, salt, variant, payload = row
            return Record(id=id, salt=salt, variant=Variant(variant), payload=payload)
