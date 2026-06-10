"""The identity a Google login resolves to.

A plain value object (not a port): the Google OAuth adapter in `platform/auth`
builds one of these and hands it to the user domain. External OAuth itself is
exercised via the real Google flow (or the dev-login path in tests).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    subject: str  # Google's stable unique id for this user
    email: str
    name: str | None = None
    picture: str | None = None
