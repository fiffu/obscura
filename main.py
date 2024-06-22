from argparse import ArgumentParser
from dataclasses import dataclass

from fastapi import FastAPI
import uvicorn

from obscura.api.controller import Controller
from obscura.db import Database
from obscura.service import Service
from obscura.logger import log, LOGGING_CONFIG
from obscura.process import PROCESS

@dataclass
class Args:
    port: int


def build_app() -> FastAPI:
    kwargs = {}

    if PROCESS.ENV.is_prod:
        kwargs.update({
            'docs_url': None,
            'redoc_url': None,
        })
        log.info('Disabling documentation in prod env')

    app = FastAPI(
        **kwargs
    )

    return app

def start_api(args: Args, db: Database):
    service = Service(db)
    ctrl = Controller(service)

    app = build_app()
    app.include_router(ctrl.router())

    uvicorn.run(app, port=args.port, log_config=LOGGING_CONFIG)


def main(args: Args):
    db = Database(PROCESS.DATABASE_URL)
    start_api(args, db)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--port', default=8000)

    parsed = parser.parse_args().__dict__
    main(Args(**parsed))