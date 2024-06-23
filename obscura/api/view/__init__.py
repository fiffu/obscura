from typing import Mapping

from fastapi.responses import HTMLResponse

from obscura.model import Variant
from obscura.api.view import strategies


class Renderer:
    VARIANT_STRATEGIES = {
        Variant.google_form_embed: strategies.GoogleFormEmbed,
    }

    @classmethod
    def render(cls, variant: Variant, payload: str) -> strategies.Rendered:
        klass = cls.VARIANT_STRATEGIES.get(variant, strategies.Strategy)
        strategy: strategies.Strategy = klass(variant)
        return strategy.render(payload)
