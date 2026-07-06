from app.core.notes.service import NoteService
from app.infra.vault.repository import VaultRepository


def test_parse_handles_json_fence() -> None:
    parsed = NoteService._parse('```json\n{"folder": "Идеи", "title": "T", "body": "B"}\n```')

    assert parsed.folder == "Идеи"
    assert parsed.title == "T"
    assert parsed.body == "B"


def test_parse_invalid_returns_empty() -> None:
    parsed = NoteService._parse("это не json")

    assert parsed.folder == ""
    assert parsed.title == ""


def test_write_and_search(tmp_path) -> None:
    vault = VaultRepository(str(tmp_path))
    saved = vault.write_note("Идеи", "Бензин-приложение", "искать заправки")

    assert saved.folder == "Идеи"
    found = vault.search(["заправки"], limit=3)
    assert found and "заправки" in found[0][1]


def test_write_note_avoids_overwrite(tmp_path) -> None:
    vault = VaultRepository(str(tmp_path))
    first = vault.write_note("Идеи", "Тема", "one")
    second = vault.write_note("Идеи", "Тема", "two")

    assert first.path != second.path
