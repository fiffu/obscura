from dataclasses import dataclass
from typing import Union

from obscura.errors import AppError
from obscura.model import Variant

from fastapi.responses import HTMLResponse


ResponseClass = Union[HTMLResponse]


@dataclass
class Rendered:
    klass: ResponseClass
    body: str


class UnsupportedVariantError(AppError):
    """Unable to render this variant."""


class Strategy:
    def __init__(self, variant: Variant):
        self.variant = variant

    def render(self, payload: str) -> Rendered:
        raise UnsupportedVariantError(variant=self.variant)


class GoogleFormEmbed(Strategy):
    def render(self, payload: str) -> Rendered:
        return Rendered(
            klass=HTMLResponse,
            body=self.templated(payload),            
        )
    
    @staticmethod
    def templated(embed_html: str):
        return '''
            <html>
                <head>
                    <style>
                        iframe {{
                            width: 100% !important;
                            height: 100% !important;
                        }}
                    </style>
                </head>
                <body style="height: 100%; width: 100%">
                    {embed_html}
                </body>
            </html>
        '''.format(embed_html=embed_html)
