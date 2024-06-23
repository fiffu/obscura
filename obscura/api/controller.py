from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse

from obscura.api import deps
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
            except (SlugExpiredError, SlugNotFoundError):
                raise HTTPException(status_code=404)

            return record.payload

        @router.post('/submit', dependencies=[Depends(deps.require_api_token)])
        def handle_submit(
            kind: Variant,
            payload: str,
        ):
            slugs = self.service.save(kind, payload)
            return slugs

        return router
