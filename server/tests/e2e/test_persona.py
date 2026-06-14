"""E2E: the 'about you' personalization questionnaire."""

from httpx import AsyncClient


async def test_persona_starts_empty_then_tracks_completion(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})

    initial = (await client.get("/api/v1/me/persona")).json()
    assert initial["percent"] == 0
    assert initial["answered"] == 0
    assert initial["total"] >= 6
    assert all(q["answer"] == "" for q in initial["questions"])

    # Answer two questions.
    updated = (
        await client.put(
            "/api/v1/me/persona",
            json={"answers": {"tabs_spaces": "Spaces", "spirit_lang": "Python"}},
        )
    ).json()
    assert updated["answered"] == 2
    assert updated["percent"] == round(2 / updated["total"] * 100)
    answers = {q["key"]: q["answer"] for q in updated["questions"]}
    assert answers["tabs_spaces"] == "Spaces"
    assert answers["spirit_lang"] == "Python"

    # Partial updates merge (don't wipe) and unknown keys are ignored.
    merged = (
        await client.put(
            "/api/v1/me/persona",
            json={"answers": {"pace": "Weekend warrior", "bogus_key": "ignored"}},
        )
    ).json()
    final = {q["key"]: q["answer"] for q in merged["questions"]}
    assert final["tabs_spaces"] == "Spaces"  # preserved
    assert final["pace"] == "Weekend warrior"
    assert "bogus_key" not in final
    assert merged["answered"] == 3
