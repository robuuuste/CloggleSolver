from dataclasses import dataclass, field
from enum import Enum


class PriceRelation(Enum):
    LOWER = "lower"
    EQUAL = "equal"
    HIGHER = "higher"


class Match(Enum):
    MATCH = "match"
    NO_MATCH = "no_match"


@dataclass
class Item:
    name: str
    id: int | None = None

    price: float | None = None
    tradeable: bool | None = None
    equipment_slot: str | None = None

    categories: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)
    regions: set[str] = field(default_factory=set)


@dataclass
class Feedback:
    tradeable: Match
    price: PriceRelation
    equipment_slot: Match
    region: Match
    category: Match
    source: Match
    name: Match