from pathlib import Path

from app.core.notes.dto import SavedNote
from app.infra.vault.constants import FALLBACK_NAME, INVALID_CHARS, MAX_TITLE_LEN


class VaultRepository:
    def __init__(self, vault_path: str) -> None:
        self._root = Path(vault_path)

    def list_folders(self) -> list[str]:
        if not self._root.exists():
            return []
        return sorted(
            item.name
            for item in self._root.iterdir()
            if item.is_dir() and not item.name.startswith(".")
        )

    def write_note(self, folder: str, title: str, body: str) -> SavedNote:
        folder_dir = self._root / folder
        folder_dir.mkdir(parents=True, exist_ok=True)
        path = self._unique_path(folder_dir, self._safe_name(title))
        path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
        return SavedNote(folder=folder, title=title, path=str(path))

    def search(self, keywords: list[str], limit: int) -> list[tuple[str, str]]:
        if not keywords:
            return []
        scored: list[tuple[int, str, str]] = []
        for md in self._root.rglob("*.md"):
            text = md.read_text(encoding="utf-8", errors="ignore")
            low = text.lower()
            score = sum(low.count(keyword) for keyword in keywords)
            if score:
                scored.append((score, md.stem, text))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [(title, text) for _, title, text in scored[:limit]]

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
