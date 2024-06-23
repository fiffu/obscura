from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Response
from fastapi.responses import PlainTextResponse, RedirectResponse

from obscura.api import deps
from obscura.logger import log
from obscura.model import Variant
from obscura.process import PROCESS
from obscura.service import Service, SlugExpiredError, SlugNotFoundError

class Controller:
    def __init__(self, service: Service):
        self.service = service

    def router(self) -> APIRouter:
        router = APIRouter()

        if PROCESS.ENV.is_dev:
            @router.get('/', response_class=RedirectResponse, include_in_schema=False)
            def redirect_to_docs():
                return '/docs'

        @router.get('/{slug}', response_class=PlainTextResponse)
        def handle_slug(slug: str):
            try:
                record = self.service.recover(slug)
                return record.payload
            except (SlugExpiredError, SlugNotFoundError) as err:
                log.info("%s: %s", err.__class__.__name__, slug)
                return Response(status_code=404)
            except:
                return Response(status_code=404)


        @router.post('/submit', dependencies=[Depends(deps.require_api_token)])
        def handle_submit(
            kind: Variant,
            payload: str,
        ):
            record = self.service.save(kind, payload)
            slugs = self.service.generate_daily_slugs(record, 7)
            return slugs

        return router
