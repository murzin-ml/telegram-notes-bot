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


def test_write_and_read(tmp_path) -> None:
    vault = VaultRepository(str(tmp_path))
    saved = vault.write_note("maksim", "Идеи", "Бензин-приложение", "искать заправки")

    assert saved.folder == "Идеи"
    notes = vault.read_all("maksim")
    assert any("заправки" in text for _, text in notes)


def test_write_note_avoids_overwrite(tmp_path) -> None:
    vault = VaultRepository(str(tmp_path))
    first = vault.write_note("maksim", "Идеи", "Тема", "one")
    second = vault.write_note("maksim", "Идеи", "Тема", "two")

    assert first.path != second.path


def test_users_are_separated(tmp_path) -> None:
    vault = VaultRepository(str(tmp_path))
    vault.write_note("maksim", "О себе", "Имя", "Максим")
    vault.write_note("valya", "О себе", "Имя", "Валя")

    maksim_texts = " ".join(text for _, text in vault.read_all("maksim"))
    valya_texts = " ".join(text for _, text in vault.read_all("valya"))

    assert "Максим" in maksim_texts and "Валя" not in maksim_texts
    assert "Валя" in valya_texts and "Максим" not in valya_texts
