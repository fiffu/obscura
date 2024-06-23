from dataclasses import dataclass
from enum import Enum


class Variant(str, Enum):
    google_form_embed = 'gform-embed'

@dataclass
class Record:
    id: str
    salt: str
    variant: Variant
    payload: str
