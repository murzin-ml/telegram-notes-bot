from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class NoteDraft:
    folder: str
    title: str
    body: str


@dataclass(slots=True, frozen=True)
class SavedNote:
    folder: str
    title: str
    path: str
