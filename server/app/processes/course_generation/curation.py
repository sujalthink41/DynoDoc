"""Reference curation — research real links for a lecture via the ResourceCurator."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.models import Lecture, Reference
from app.domains.course.repository import add_reference
from app.shared.contracts.curation import ResourceCurator


async def generate_lecture_references(
    session: AsyncSession, *, curator: ResourceCurator, lecture: Lecture
) -> list[Reference]:
    drafts = await curator.find_references(
        lecture_title=lecture.title, summary=lecture.summary, topics=lecture.topics
    )

    references: list[Reference] = []
    for position, draft in enumerate(drafts, start=1):
        references.append(
            await add_reference(
                session,
                lecture_id=lecture.id,
                position=position,
                type=draft.type,
                url=draft.url,
                title=draft.title,
            )
        )

    logger.bind(lecture_id=str(lecture.id), references=len(references)).info(
        "lecture references curated"
    )
    return references
