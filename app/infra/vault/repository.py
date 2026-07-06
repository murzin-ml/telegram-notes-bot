from pathlib import Path

from app.core.notes.dto import SavedNote
from app.infra.vault.constants import FALLBACK_NAME, INVALID_CHARS, MAX_TITLE_LEN


class VaultRepository:
    def __init__(self, base_path: str) -> None:
        self._base = Path(base_path)

    def list_folders(self, user_key: str) -> list[str]:
        root = self._user_root(user_key)
        if not root.exists():
            return []
        return sorted(
            item.name
            for item in root.iterdir()
            if item.is_dir() and not item.name.startswith(".")
        )

    def write_note(self, user_key: str, folder: str, title: str, body: str) -> SavedNote:
        folder_dir = self._user_root(user_key) / folder
        folder_dir.mkdir(parents=True, exist_ok=True)
        path = self._unique_path(folder_dir, self._safe_name(title))
        path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
        return SavedNote(folder=folder, title=title, path=str(path))

    def read_all(self, user_key: str) -> list[tuple[str, str]]:
        root = self._user_root(user_key)
        if not root.exists():
            return []
        return [
            (md.stem, md.read_text(encoding="utf-8", errors="ignore"))
            for md in sorted(root.rglob("*.md"))
        ]

    def _user_root(self, user_key: str) -> Path:
        return self._base / user_key

    @staticmethod
    def _safe_name(title: str) -> str:
        cleaned = INVALID_CHARS.sub(" ", title).strip()
        return cleaned[:MAX_TITLE_LEN].strip() or FALLBACK_NAME

    @staticmethod
    def _unique_path(folder_dir: Path, base: str) -> Path:
        path = folder_dir / f"{base}.md"
        counter = 2
        while path.exists():
            path = folder_dir / f"{base} ({counter}).md"
            counter += 1
        return path
