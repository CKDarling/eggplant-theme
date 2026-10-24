from __future__ import annotations

import json
from dataclasses import dataclass

MAX_RETRIES = 3  # give up after three attempts
_cache: dict[str, int] = {}


@dataclass(frozen=True)
class Order:
    """A single eggplant order, priced in cents."""

    name: str
    cups: int = 1
    note: str | None = None

    def total(self, price: int = 350) -> int:
        # Bulk orders get ten percent off
        if self.cups >= 10:
            return int(self.cups * price * 0.9)
        return self.cups * price


def summarize(orders: list[Order]) -> str:
    global _cache
    lines = [f"{o.name}\t{o.total()}" for o in orders]
    data = {"name": "Eggplant", "count": len(orders)}
    print(data["name"], data["count"] > 0)
    return "\n".join(lines)


if __name__ == "__main__":
    print(summarize([Order("Ada", cups=12)]))
    print(json.dumps({"retries": MAX_RETRIES}))
