"""DynoDoc merch rewards — redeemed by spending DynoCoins (deducts the balance)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Reward:
    key: str
    title: str
    emoji: str
    cost: int


REWARDS: list[Reward] = [
    Reward("diary", "Diary + Pen", "📔", 1000),
    Reward("bottle", "DynoDoc Bottle", "🍶", 2000),
    Reward("tshirt", "DynoDoc T-shirt", "👕", 5000),
    Reward("bag", "DynoDoc Bag", "🎒", 10000),
]

_BY_KEY = {r.key: r for r in REWARDS}


def get_reward(key: str) -> Reward | None:
    return _BY_KEY.get(key)
