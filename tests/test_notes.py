from app.core.notes.service import NoteService
from app.infra.vault.repository import VaultRepository


def test_parse_splits_header_and_body() -> None:
    raw = '{"folder": "Идеи", "title": "T", "update_of": ""}\n===BODY===\nтело заметки'
    header, body = NoteService._parse(raw)

    assert header.folder == "Идеи"
    assert header.title == "T"
    assert body == "тело заметки"


def test_parse_keeps_verbatim_body_with_quotes() -> None:
    raw = (
        '{"folder": "Знания", "title": "Схема", "update_of": ""}\n===BODY===\n'
        'flowchart TD\n  D["узел"] --> E["другой"]'
    )
    header, body = NoteService._parse(raw)

    assert header.folder == "Знания"
    assert 'D["узел"]' in body and "flowchart TD" in body


def test_parse_invalid_header_still_keeps_body() -> None:
    header, body = NoteService._parse("не json\n===BODY===\nтело")

    assert header.folder == ""
    assert body == "тело"


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


def test_find_and_overwrite(tmp_path) -> None:
    vault = VaultRepository(str(tmp_path))
    vault.write_note("maksim", "О себе", "Машина", "Hyundai")

    found = vault.find_note("maksim", "Машина")
    assert found is not None
    vault.overwrite(found, "Машина", "Kia")

    texts = " ".join(text for _, text in vault.read_all("maksim"))
    assert "Kia" in texts and "Hyundai" not in texts
