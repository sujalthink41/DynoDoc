"""The 'about you' personalization questionnaire — fun, optional, anytime.

Answers are stored as { key: value } and fed into future personalization. The
catalog here is the single source of truth (so the completion % is consistent).
"""

from dataclasses import dataclass, field

from app.domains.user.dtos import PersonaQuestionView, PersonaView


@dataclass(frozen=True)
class PersonaQuestion:
    key: str
    prompt: str
    emoji: str
    kind: str  # "choice" | "text"
    options: tuple[str, ...] = field(default_factory=tuple)
    allow_custom: bool = False  # choice questions where the learner may type their own


QUESTIONS: list[PersonaQuestion] = [
    PersonaQuestion(
        "goal_vibe",
        "Why are you leveling up your tech skills?",
        "🎯",
        "choice",
        (
            "Land a new job",
            "Level up at work",
            "Build a side project",
            "Pure curiosity",
            "World domination",
        ),
    ),
    PersonaQuestion(
        "spirit_lang",
        "Your spirit programming language?",
        "🦖",
        "choice",
        ("Python", "JavaScript", "TypeScript", "Rust", "Go", "Java", "C++", "SQL"),
        allow_custom=True,
    ),
    PersonaQuestion(
        "learn_time",
        "When does your brain work best?",
        "⏰",
        "choice",
        ("Early bird 🌅", "Midday grind ☀️", "Night owl 🌙", "Totally random 🎲"),
    ),
    PersonaQuestion(
        "kryptonite",
        "What usually trips you up when learning?",
        "😵‍💫",
        "choice",
        (
            "Maths & theory",
            "Staying consistent",
            "Too many open tabs",
            "Tutorial hell",
            "Nothing — I'm him",
        ),
    ),
    PersonaQuestion(
        "tabs_spaces",
        "The eternal question: tabs or spaces?",
        "⌨️",
        "choice",
        ("Tabs", "Spaces", "Both, to watch the world burn"),
    ),
    PersonaQuestion(
        "pace",
        "Your ideal learning pace?",
        "🐢",
        "choice",
        ("Slow & steady", "Weekend warrior", "Sprint then crash", "Beast mode, daily"),
    ),
    PersonaQuestion("dream_build", "What do you dream of building?", "🚀", "text"),
    PersonaQuestion("fun_fact", "Drop a fun fact about yourself", "🎈", "text"),
]

_KEYS = {q.key for q in QUESTIONS}


def known_keys() -> set[str]:
    return _KEYS


def build_view(answers: dict[str, str]) -> PersonaView:
    questions = [
        PersonaQuestionView(
            key=q.key,
            prompt=q.prompt,
            emoji=q.emoji,
            kind=q.kind,
            options=list(q.options),
            allow_custom=q.allow_custom,
            answer=answers.get(q.key, ""),
        )
        for q in QUESTIONS
    ]
    answered = sum(1 for q in QUESTIONS if answers.get(q.key, "").strip())
    total = len(QUESTIONS)
    return PersonaView(
        questions=questions,
        answered=answered,
        total=total,
        percent=round(answered / total * 100) if total else 0,
    )
