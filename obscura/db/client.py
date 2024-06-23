from collections import OrderedDict
from functools import cached_property
from pathlib import Path
import re
import sqlite3

from obscura.logger import component_logger


class Client(sqlite3.Connection):
    log = component_logger('db')
    migrations_dir = Path(__file__).parent / 'migrations'
    migrations_table = ''
    whitespace = re.compile('\\s+')

    @classmethod
    def connect(cls, dsn):
        return cls(dsn, check_same_thread=False)

    def execute(self, sql, *params):
        self.log.info('execute: %s', self.compact(sql))
        if params:
            self.log.debug(' params: %s', params)
        return super().execute(sql, params)

    @classmethod
    def compact(cls, sql: str) -> str:
        return cls.whitespace.sub(' ', sql).strip()

    @cached_property
    def migrations(self) -> OrderedDict[str, str]:
        migrations = OrderedDict()
        for path in sorted(self.migrations_dir.iterdir()):
            if path.is_dir():
                continue
            with open(path, encoding='utf-8') as file:
                version = path.name
                migrations[version] = file.read()
        return migrations

    def ensure_migrations_table(self):
        self.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations(
                version TEXT PRIMARY KEY
            )
        ''')

    def find_pending_migrations(self):
        applied_migrations: list[str] = [
            row[0] for row in self.execute('SELECT version FROM schema_migrations ORDER BY version ASC')
        ]

        defined_migrations = self.migrations
        pending_migrations = defined_migrations.copy()

        # Ensure that applied migrations match definitions, and remove them from pending list
        for applied, defined in zip(applied_migrations, defined_migrations.keys()):
            if applied not in defined_migrations:
                raise ValueError(f'found applied migrations that are not defined: {applied}')
            if applied != defined:
                raise ValueError(f'found applied migrations in divergent order, expected: {defined}, got: {applied}')
            pending_migrations.pop(applied)

        return pending_migrations

    def migrate(self):
        self.ensure_migrations_table()

        pending_migrations = self.find_pending_migrations()

        with self as tx:
            for (version, sql) in pending_migrations.items():
                tx.executescript(sql)
                tx.execute('INSERT INTO schema_migrations(version) values (?)', version)
                self.log.info(f'Applied migration {version}')
