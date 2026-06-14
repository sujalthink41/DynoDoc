"""Request schema for redeeming a merch reward."""

from pydantic import BaseModel


class RedeemRequest(BaseModel):
    """Where to ship the reward."""

    address: str
