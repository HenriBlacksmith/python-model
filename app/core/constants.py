from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class Constants:
    name: str = "Sample API"

    @cached_property
    def version(self) -> str:
        with open("VERSION") as f:
            return f.read().strip()


constants = Constants()
