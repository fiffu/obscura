from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse

from obscura import errors
from obscura.api import deps
from obscura.logger import log
from obscura.model import Variant
from obscura.process import PROCESS
from obscura.service import Service
from obscura.api.view import Renderer

class Controller:
    def __init__(self, service: Service):
        self.service = service

    def router(self) -> APIRouter:
        router = APIRouter()

        if PROCESS.ENV.is_dev:
            @router.get('/', response_class=RedirectResponse, include_in_schema=False)
            def redirect_to_docs():
                return '/docs'

        @router.get('/{slug}')
        def handle_slug(slug: str):
            try:
                record = self.service.recover(slug)
                reply = Renderer.render(record.variant, record.payload)
                return reply.klass(reply.body)

            except errors.AppError as err:
                log.info("%s, slug=%s meta=%s", err, slug, err.metadata)
                return Response(status_code=404)
            except Exception as err:
                log.error("Uncaught error: %s, slug=%s", err, slug)
                return Response(status_code=404)

        @router.post('/submit', dependencies=[Depends(deps.require_api_token)])
        def handle_submit(variant: Variant, payload: str):
            record = self.service.save(variant, payload)
            slugs = self.service.generate_daily_slugs(record, 7)
            return slugs

        return router
