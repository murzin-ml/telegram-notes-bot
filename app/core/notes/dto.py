from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SavedNote:
    folder: str
    title: str
    path: str


@dataclass(slots=True, frozen=True)
class CaptureResult:
    folder: str
    title: str
    updated: bool
