"""Connections — a curated, generic daily grouping puzzle (NYT/LinkedIn style).

16 tiles hide 4 groups of 4. The puzzle is the SAME for everyone on a given day,
selected by weekday so difficulty ramps across the week (gentle on Sunday →
expert on Saturday), with the week number rotating which puzzle of that tier
appears. Tiles are shuffled deterministically so every player sees one board.
"""

import random
from dataclasses import dataclass
from datetime import date

GAME_KEY = "connections"

# Sunday(0) → Saturday(6): difficulty tier (1 gentle .. 5 expert), ramping up.
_WEEKDAY_TIER = [1, 2, 2, 3, 3, 4, 5]
_DIFFICULTY_LABEL = {1: "Gentle", 2: "Easy", 3: "Moderate", 4: "Tough", 5: "Expert"}


@dataclass(frozen=True)
class ConnGroup:
    label: str
    level: int  # 0 (easiest) .. 3 (trickiest) — drives tile colours
    members: tuple[str, str, str, str]


@dataclass(frozen=True)
class ConnPuzzle:
    difficulty: int  # 1 (gentle) .. 5 (expert)
    groups: tuple[ConnGroup, ConnGroup, ConnGroup, ConnGroup]


PUZZLES: list[ConnPuzzle] = [
    ConnPuzzle(
        1,
        (
            ConnGroup("HTTP status codes", 0, ("200", "301", "404", "500")),
            ConnGroup("Boolean operators", 1, ("And", "Or", "Not", "Xor")),
            ConnGroup("Linux commands", 2, ("Grep", "Chmod", "Kill", "Mount")),
            ConnGroup("SemVer parts", 3, ("Major", "Minor", "Patch", "Build")),
        ),
    ),
    ConnPuzzle(
        1,
        (
            ConnGroup("Python data types", 0, ("List", "Tuple", "Dict", "Set")),
            ConnGroup("Loop keywords", 1, ("For", "While", "Break", "Continue")),
            ConnGroup("Primitive types", 2, ("Int", "Float", "Bool", "Char")),
            ConnGroup("Markup & style", 3, ("HTML", "CSS", "XML", "SVG")),
        ),
    ),
    ConnPuzzle(
        2,
        (
            ConnGroup("Sorting algorithms", 0, ("Quick", "Merge", "Bubble", "Heap")),
            ConnGroup("JavaScript frameworks", 1, ("React", "Angular", "Svelte", "Vue")),
            ConnGroup("SQL clauses", 2, ("Select", "Where", "Having", "Limit")),
            ConnGroup("Container tools", 3, ("Docker", "Podman", "Kubernetes", "Helm")),
        ),
    ),
    ConnPuzzle(
        2,
        (
            ConnGroup("Array methods", 0, ("Map", "Filter", "Reduce", "Slice")),
            ConnGroup("React hooks", 1, ("State", "Effect", "Memo", "Ref")),
            ConnGroup("Network protocols", 2, ("TCP", "UDP", "HTTP", "FTP")),
            ConnGroup("Editors & IDEs", 3, ("Vim", "Emacs", "Nano", "Code")),
        ),
    ),
    ConnPuzzle(
        3,
        (
            ConnGroup("Data structures", 0, ("Stack", "Queue", "Graph", "Trie")),
            ConnGroup("CSS units", 1, ("Pixel", "Percent", "Rem", "Viewport")),
            ConnGroup("NoSQL databases", 2, ("Mongo", "Redis", "Cassandra", "Couch")),
            ConnGroup("OSI layers", 3, ("Physical", "Session", "Transport", "Network")),
        ),
    ),
    ConnPuzzle(
        3,
        (
            ConnGroup("HTTP methods", 0, ("Get", "Post", "Patch", "Delete")),
            ConnGroup("Access modifiers", 1, ("Public", "Private", "Protected", "Internal")),
            ConnGroup("HTTP headers", 2, ("Accept", "Cookie", "Origin", "Referer")),
            ConnGroup("CI/CD tools", 3, ("Jenkins", "Actions", "CircleCI", "Travis")),
        ),
    ),
    ConnPuzzle(
        4,
        (
            ConnGroup("Python keywords", 0, ("Lambda", "Yield", "Assert", "Import")),
            ConnGroup("Cloud providers", 1, ("Azure", "Vercel", "Heroku", "Render")),
            ConnGroup("Design patterns", 2, ("Singleton", "Factory", "Observer", "Adapter")),
            ConnGroup("Hashing algorithms", 3, ("MD5", "SHA", "Bcrypt", "Argon")),
        ),
    ),
    ConnPuzzle(
        4,
        (
            ConnGroup("Git commands", 0, ("Clone", "Rebase", "Stash", "Cherry")),
            ConnGroup("Message queues", 1, ("Kafka", "RabbitMQ", "SQS", "NATS")),
            ConnGroup("Big-O classes", 2, ("Constant", "Linear", "Quadratic", "Logarithmic")),
            ConnGroup("Front-end build tools", 3, ("Webpack", "Vite", "Rollup", "Parcel")),
        ),
    ),
    ConnPuzzle(
        5,
        (
            ConnGroup("REST verbs", 0, ("Put", "Post", "Head", "Options")),
            ConnGroup("Python web frameworks", 1, ("Django", "Flask", "FastAPI", "Tornado")),
            ConnGroup("Database keys", 2, ("Primary", "Foreign", "Unique", "Composite")),
            ConnGroup("Cryptography terms", 3, ("Cipher", "Nonce", "Salt", "Hash")),
        ),
    ),
    ConnPuzzle(
        5,
        (
            ConnGroup("AWS services", 0, ("Lambda", "Fargate", "Athena", "Glue")),
            ConnGroup("Version control", 1, ("Git", "Mercurial", "Subversion", "Perforce")),
            ConnGroup("Typed languages", 2, ("Rust", "Swift", "Kotlin", "Scala")),
            ConnGroup("Pointer-ish things", 3, ("Reference", "Address", "Handle", "Cursor")),
        ),
    ),
]


def _sunday_index(day: date) -> int:
    """0 = Sunday .. 6 = Saturday (Python's weekday() is Mon=0..Sun=6)."""
    return (day.weekday() + 1) % 7


def puzzle_for_date(day: date) -> ConnPuzzle:
    tier = _WEEKDAY_TIER[_sunday_index(day)]
    candidates = [p for p in PUZZLES if p.difficulty == tier] or PUZZLES
    week = day.toordinal() // 7
    return candidates[(week + _sunday_index(day)) % len(candidates)]


def difficulty_label(puzzle: ConnPuzzle) -> str:
    return _DIFFICULTY_LABEL.get(puzzle.difficulty, "Moderate")


def daily_tiles(puzzle: ConnPuzzle, day: date) -> list[str]:
    """All 16 tiles, shuffled deterministically so everyone sees the same board."""
    tiles = [member for group in puzzle.groups for member in group.members]
    random.Random(day.toordinal()).shuffle(tiles)
    return tiles


def grade(puzzle: ConnPuzzle, guesses: list[list[str]]) -> int:
    """Count how many of the learner's 4 guessed groups exactly match an answer group."""
    answers = {frozenset(group.members) for group in puzzle.groups}
    return sum(1 for guess in guesses if frozenset(guess) in answers)
